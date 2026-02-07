import json
import re
from pathlib import Path
from typing import Any
from datetime import datetime

from .base import (
    BaseParser,
    ParsedDocument,
    DocumentCategory,
    DocumentType
)


class JSONParser(BaseParser):
    """Parser for JSON files including AI chat logs and Kiro IDE logs."""
    
    supported_extensions = ['.json', '.jsonl']
    
    # Command patterns for extraction
    COMMAND_PATTERNS = {
        'git': r'git\s+[a-z]+(?:\s+[^\n;|&]+)?',
        'docker': r'docker(?:-compose)?\s+[a-z]+(?:\s+[^\n;|&]+)?',
        'aws': r'aws\s+[a-z0-9-]+(?:\s+[^\n;|&]+)?',
        'kubectl': r'kubectl\s+[a-z]+(?:\s+[^\n;|&]+)?',
        'npm': r'npm\s+[a-z]+(?:\s+[^\n;|&]+)?',
        'pip': r'pip\s+[a-z]+(?:\s+[^\n;|&]+)?',
        'powershell': r'(?:Get|Set|New|Remove|Invoke)-[A-Za-z]+(?:\s+[^\n;|&]+)?'
    }
    
    def parse(self, filepath: Path) -> ParsedDocument:
        """Parse JSON file and extract structured content."""
        try:
            content = filepath.read_text(encoding='utf-8')
            
            # Handle JSONL (JSON Lines)
            if filepath.suffix == '.jsonl':
                data = [json.loads(line) for line in content.strip().split('\n') if line.strip()]
            else:
                data = json.loads(content)
            
            # Detect category and extract accordingly
            category = self.detect_category(filepath, content)
            
            if category == DocumentCategory.AI_CHAT_HISTORY:
                return self._parse_ai_chat(filepath, data, content)
            elif category == DocumentCategory.KIRO_IDE_LOGS:
                return self._parse_kiro_logs(filepath, data, content)
            else:
                return self._parse_generic_json(filepath, data, content)
            
        except Exception as e:
            return ParsedDocument(
                id=self.generate_id(filepath),
                filename=filepath.name,
                filepath=str(filepath),
                category=DocumentCategory.GENERAL,
                doc_type=DocumentType.JSON,
                raw_text="",
                parse_success=False,
                error_message=str(e)
            )
    
    def _parse_ai_chat(self, filepath: Path, data: Any, raw_content: str) -> ParsedDocument:
        """Parse AI chat history with analysis."""
        messages = self._extract_messages(data)
        
        # Extract commands from messages
        all_commands = []
        for msg in messages:
            if msg.get('role') in ['assistant', 'model']:
                commands = self._extract_commands(msg.get('content', ''))
                all_commands.extend(commands)
        
        # Build readable text
        text_parts = []
        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', '')
            text_parts.append(f"[{role.upper()}] {timestamp}\n{content}")
        
        raw_text = "\n\n---\n\n".join(text_parts)
        
        # Detect AI platform
        platform = self._detect_ai_platform(filepath, data)
        
        metadata = {
            'platform': platform,
            'message_count': len(messages),
            'user_messages': len([m for m in messages if m.get('role') == 'user']),
            'assistant_messages': len([m for m in messages if m.get('role') in ['assistant', 'model']]),
            'extracted_commands': all_commands[:50],  # Limit
            'command_types': list(set(cmd['type'] for cmd in all_commands)),
            'file_size_bytes': filepath.stat().st_size
        }
        
        return ParsedDocument(
            id=self.generate_id(filepath),
            filename=filepath.name,
            filepath=str(filepath),
            category=DocumentCategory.AI_CHAT_HISTORY,
            doc_type=DocumentType.JSON,
            raw_text=raw_text,
            chunks=self.chunk_text(raw_text),
            metadata=metadata,
            parse_success=True
        )
    
    def _parse_kiro_logs(self, filepath: Path, data: Any, raw_content: str) -> ParsedDocument:
        """Parse Kiro IDE logs with task extraction."""
        logs = data if isinstance(data, list) else [data]
        
        tasks = []
        total_credits = 0
        total_time_seconds = 0
        
        for entry in logs:
            task = {
                'task_id': entry.get('task_id', entry.get('id', '')),
                'status': entry.get('status', 'unknown'),
                'credits_used': entry.get('credits', entry.get('credits_used', 0)),
                'time_spent': entry.get('duration', entry.get('time_spent', 0)),
                'description': entry.get('description', entry.get('task', '')),
                'timestamp': entry.get('timestamp', entry.get('created_at', ''))
            }
            tasks.append(task)
            total_credits += task['credits_used'] or 0
            total_time_seconds += task['time_spent'] or 0
        
        # Build readable text
        text_parts = []
        for task in tasks:
            text_parts.append(
                f"Task: {task['task_id']}\n"
                f"Status: {task['status']}\n"
                f"Credits: {task['credits_used']}\n"
                f"Time: {task['time_spent']}s\n"
                f"Description: {task['description']}"
            )
        
        raw_text = "\n\n---\n\n".join(text_parts)
        
        # Calculate statistics
        status_counts = {}
        for task in tasks:
            status = task['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        metadata = {
            'task_count': len(tasks),
            'total_credits_used': total_credits,
            'total_time_seconds': total_time_seconds,
            'total_time_hours': round(total_time_seconds / 3600, 2),
            'status_breakdown': status_counts,
            'tasks': tasks[:100],  # Limit for metadata
            'file_size_bytes': filepath.stat().st_size
        }
        
        return ParsedDocument(
            id=self.generate_id(filepath),
            filename=filepath.name,
            filepath=str(filepath),
            category=DocumentCategory.KIRO_IDE_LOGS,
            doc_type=DocumentType.JSON,
            raw_text=raw_text,
            chunks=self.chunk_text(raw_text),
            metadata=metadata,
            parse_success=True
        )
    
    def _parse_generic_json(self, filepath: Path, data: Any, raw_content: str) -> ParsedDocument:
        """Parse generic JSON files."""
        # Pretty print for readability
        raw_text = json.dumps(data, indent=2, default=str)
        
        metadata = self.extract_metadata(filepath)
        metadata['structure_type'] = 'array' if isinstance(data, list) else 'object'
        metadata['item_count'] = len(data) if isinstance(data, list) else len(data.keys()) if isinstance(data, dict) else 1
        
        return ParsedDocument(
            id=self.generate_id(filepath),
            filename=filepath.name,
            filepath=str(filepath),
            category=DocumentCategory.GENERAL,
            doc_type=DocumentType.JSON,
            raw_text=raw_text,
            chunks=self.chunk_text(raw_text),
            metadata=metadata,
            parse_success=True
        )
    
    def _extract_messages(self, data: Any) -> list[dict]:
        """Extract messages from various chat export formats."""
        messages = []
        
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    if 'role' in item or 'author' in item:
                        messages.append({
                            'role': item.get('role', item.get('author', {}).get('role', 'unknown')),
                            'content': item.get('content', item.get('text', item.get('message', ''))),
                            'timestamp': item.get('timestamp', item.get('create_time', ''))
                        })
        
        elif isinstance(data, dict):
            # Handle nested structures
            if 'messages' in data:
                return self._extract_messages(data['messages'])
            if 'conversation' in data:
                return self._extract_messages(data['conversation'])
            if 'mapping' in data:  # ChatGPT format
                for node in data['mapping'].values():
                    if 'message' in node and node['message']:
                        msg = node['message']
                        messages.append({
                            'role': msg.get('author', {}).get('role', 'unknown'),
                            'content': msg.get('content', {}).get('parts', [''])[0] if isinstance(msg.get('content', {}).get('parts'), list) else '',
                            'timestamp': msg.get('create_time', '')
                        })
        
        return messages
    
    def _extract_commands(self, text: str) -> list[dict]:
        """Extract CLI commands from text."""
        commands = []
        
        for cmd_type, pattern in self.COMMAND_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                commands.append({
                    'type': cmd_type,
                    'command': match.strip()
                })
        
        return commands
    
    def _detect_ai_platform(self, filepath: Path, data: Any) -> str:
        """Detect which AI platform the chat is from."""
        filename_lower = filepath.name.lower()
        
        if 'claude' in filename_lower:
            return 'claude'
        if 'copilot' in filename_lower:
            return 'copilot'
        if 'gemini' in filename_lower:
            return 'gemini'
        if 'perplexity' in filename_lower:
            return 'perplexity'
        if 'chatgpt' in filename_lower or 'openai' in filename_lower:
            return 'chatgpt'
        
        # Check data structure
        if isinstance(data, dict):
            if 'mapping' in data:
                return 'chatgpt'
        
        return 'unknown'
    
    def extract_metadata(self, filepath: Path) -> dict[str, Any]:
        """Extract JSON file metadata."""
        return {
            'file_size_bytes': filepath.stat().st_size,
            'modified_time': filepath.stat().st_mtime
        }