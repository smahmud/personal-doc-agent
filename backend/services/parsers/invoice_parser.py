import re
from pathlib import Path
from typing import Any, Optional
from decimal import Decimal, InvalidOperation

from .pdf_parser import PDFParser
from .base import (
    ParsedDocument,
    DocumentCategory
)


class InvoiceParser(PDFParser):
    """Specialized parser for car maintenance invoices."""
    
    # Service categories for classification
    SERVICE_CATEGORIES = {
        'motor': ['oil', 'engine', 'motor', 'filter', 'spark plug', 'timing belt', 'gasket'],
        'brakes': ['brake', 'pad', 'rotor', 'caliper', 'brake fluid'],
        'transmission': ['transmission', 'clutch', 'gearbox', 'differential'],
        'tires': ['tire', 'tyre', 'wheel', 'alignment', 'balance', 'rotation'],
        'electrical': ['battery', 'alternator', 'starter', 'electrical', 'fuse', 'light'],
        'suspension': ['suspension', 'shock', 'strut', 'spring', 'bushing'],
        'cooling': ['coolant', 'radiator', 'thermostat', 'water pump', 'cooling'],
        'exhaust': ['exhaust', 'muffler', 'catalytic', 'emission'],
        'body': ['body', 'paint', 'dent', 'windshield', 'wiper'],
        'inspection': ['inspection', 'diagnostic', 'check', 'test'],
        'labor': ['labor', 'labour', 'service charge', 'shop fee']
    }
    
    def parse(self, filepath: Path) -> ParsedDocument:
        """Parse invoice PDF with detailed extraction."""
        # First get base PDF parsing
        base_result = super().parse(filepath)
        
        if not base_result.parse_success:
            return base_result
        
        # Override category
        base_result.category = DocumentCategory.CAR_MAINTENANCE
        
        # Extract invoice-specific data
        invoice_data = self._extract_invoice_data(base_result.raw_text)
        
        # Update metadata with invoice details
        base_result.metadata.update({
            'invoice_number': invoice_data.get('invoice_number'),
            'invoice_date': invoice_data.get('date'),
            'dealer_name': invoice_data.get('dealer_name'),
            'vehicle_info': invoice_data.get('vehicle_info'),
            'mileage': invoice_data.get('mileage'),
            'line_items': invoice_data.get('line_items', []),
            'subtotal': invoice_data.get('subtotal'),
            'tax': invoice_data.get('tax'),
            'total': invoice_data.get('total'),
            'category_breakdown': invoice_data.get('category_breakdown', {}),
            'payment_method': invoice_data.get('payment_method')
        })
        
        return base_result
    
    def _extract_invoice_data(self, text: str) -> dict[str, Any]:
        """Extract structured data from invoice text."""
        data = {}
        
        # Invoice number
        invoice_match = re.search(
            r'(?:invoice|inv|receipt|order)[\s#:]*([A-Z0-9-]+)',
            text, re.IGNORECASE
        )
        if invoice_match:
            data['invoice_number'] = invoice_match.group(1)
        
        # Date extraction
        date_patterns = [
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s,]+\d{1,2}[\s,]+\d{4}'
        ]
        for pattern in date_patterns:
            date_match = re.search(pattern, text, re.IGNORECASE)
            if date_match:
                data['date'] = date_match.group(0)
                break
        
        # Dealer/Shop name (usually at top)
        lines = text.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if len(line) > 5 and not any(char.isdigit() for char in line[:5]):
                if any(word in line.lower() for word in ['auto', 'dealer', 'service', 'repair', 'motors', 'car']):
                    data['dealer_name'] = line
                    break
        
        # Vehicle info
        vehicle_patterns = [
            r'(\d{4})\s+([\w-]+)\s+([\w-]+)',  # Year Make Model
            r'VIN[:\s]*([A-HJ-NPR-Z0-9]{17})',
            r'License[:\s]*([A-Z0-9]+)'
        ]
        vehicle_info = {}
        for pattern in vehicle_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if 'VIN' in pattern:
                    vehicle_info['vin'] = match.group(1)
                elif 'License' in pattern:
                    vehicle_info['license'] = match.group(1)
                else:
                    vehicle_info['year'] = match.group(1)
                    vehicle_info['make'] = match.group(2)
                    vehicle_info['model'] = match.group(3)
        data['vehicle_info'] = vehicle_info
        
        # Mileage
        mileage_match = re.search(
            r'(?:mileage|odometer|miles|km)[:\s]*([0-9,]+)',
            text, re.IGNORECASE
        )
        if mileage_match:
            data['mileage'] = mileage_match.group(1).replace(',', '')
        
        # Extract line items and amounts
        line_items = self._extract_line_items(text)
        data['line_items'] = line_items
        
        # Categorize spending
        data['category_breakdown'] = self._categorize_spending(line_items)
        
        # Totals
        data['subtotal'] = self._extract_amount(text, ['subtotal', 'sub-total', 'sub total'])
        data['tax'] = self._extract_amount(text, ['tax', 'vat', 'gst', 'hst'])
        data['total'] = self._extract_amount(text, ['total', 'grand total', 'amount due', 'balance due'])
        
        # Payment method
        payment_match = re.search(
            r'(?:paid by|payment|method)[:\s]*(cash|credit|debit|visa|mastercard|amex|check)',
            text, re.IGNORECASE
        )
        if payment_match:
            data['payment_method'] = payment_match.group(1).lower()
        
        return data
    
    def _extract_line_items(self, text: str) -> list[dict]:
        """Extract individual line items from invoice."""
        line_items = []
        
        # Pattern: Description followed by amount
        # e.g., "Oil Change Service    \$45.99"
        # e.g., "Brake Pads (Front)    129.99"
        pattern = r'([A-Za-z][A-Za-z0-9\s\(\)/-]{5,50})\s+\$?([\d,]+\.?\d{0,2})'
        
        matches = re.findall(pattern, text)
        
        for desc, amount in matches:
            desc = desc.strip()
            
            # Skip if description looks like header or total line
            skip_words = ['subtotal', 'total', 'tax', 'invoice', 'date', 'phone', 'address']
            if any(word in desc.lower() for word in skip_words):
                continue
            
            try:
                amount_decimal = float(amount.replace(',', ''))
                
                # Reasonable amount filter (skip page numbers, etc.)
                if 0.01 <= amount_decimal <= 50000:
                    # Categorize the item
                    category = self._categorize_item(desc)
                    
                    line_items.append({
                        'description': desc,
                        'amount': amount_decimal,
                        'category': category
                    })
            except (ValueError, InvalidOperation):
                continue
        
        return line_items
    
    def _categorize_item(self, description: str) -> str:
        """Categorize a line item based on description."""
        desc_lower = description.lower()
        
        for category, keywords in self.SERVICE_CATEGORIES.items():
            if any(keyword in desc_lower for keyword in keywords):
                return category
        
        return 'other'
    
    def _categorize_spending(self, line_items: list[dict]) -> dict[str, float]:
        """Sum spending by category."""
        breakdown = {}
        
        for item in line_items:
            category = item.get('category', 'other')
            amount = item.get('amount', 0)
            breakdown[category] = breakdown.get(category, 0) + amount
        
        # Round values
        return {k: round(v, 2) for k, v in breakdown.items()}
    
    def _extract_amount(self, text: str, keywords: list[str]) -> Optional[float]:
        """Extract monetary amount near keywords."""
        for keyword in keywords:
            pattern = rf'{keyword}[:\s]*\$?([\d,]+\.?\d{{0,2}})'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    continue
        return None