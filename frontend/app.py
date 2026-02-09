import streamlit as st
import requests
import os

st.set_page_config(
    page_title="Personal Documentation Agent",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Personal Documentation Agent")
st.markdown("---")

# Health check
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.subheader("🔍 System Status")

try:
    response = requests.get(f"{API_URL}/health", timeout=5)
    if response.status_code == 200:
        st.success("✅ API is healthy!")
        st.json(response.json())
    else:
        st.error(f"❌ API returned status: {response.status_code}")
except requests.exceptions.ConnectionError:
    st.error("❌ Cannot connect to API. Is it running?")
except Exception as e:
    st.error(f"❌ Error: {e}")

st.markdown("---")
st.info("🚧 Full UI coming in Phase 4")