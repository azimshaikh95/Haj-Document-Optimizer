import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image
from io import BytesIO
import zipfile
import re
from datetime import datetime
import os

# Page Configuration
st.set_page_config(page_title="Haj Doc Optimizer", page_icon="🕋", layout="centered")

# --- SIDEBAR SHORTCUTS (MATCHING NATIVE UPLOAD BUTTON STYLE) ---
with st.sidebar:
    st.markdown("""
        <style>
            .sidebar-btn {
                display: block !important;
                text-align: center !important;
                background-color: #FFFFFF !important;
                color: #262730 !important;
                border: 1px solid #D3D6DF !important;
                padding: 10px 16px !important;
                border-radius: 8px !important;
                text-decoration: none !important;
                font-size: 14px !important;
                font-weight: 500 !important;
                margin-bottom: 12px !important;
                box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
                transition: background-color 0.2s, border-color 0.2s !important;
            }
            .sidebar-btn:hover {
                background-color: #F8F9FA !important;
                border-color: #A3A8B8 !important;
                color: #262730 !important;
                text-decoration: none !important;
            }
            .sidebar-section-title {
                margin-top: 15px !important;
                margin-bottom: 5px !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h2 class='sidebar-section-title'>🌐 Official Portals</h2>", unsafe_allow_html=True)
    st.write("Click below to open pages in a new tab:")
    
    st.markdown("""
        <a class="sidebar-btn" href="https://hajcommittee.gov.in/registration" target="_blank">
            📝 Registration Form
        </a>
        <a class="sidebar-btn" href="https://hajcommittee.gov.in/login" target="_blank">
            🔑 Login Page
        </a>
        <a class="sidebar-btn" href="https://gujarathajhouse.in/" target="_blank">
            🏢 Gujarat Haj House Website
        </a>
        <hr style="margin-top: 20px; margin-bottom: 20px; border-color: #D3D6DF;">
    """, unsafe_allow_html=True)

    st.markdown("<h2 class='sidebar-section-title'>🚀 Supportive Apps</h2>", unsafe_allow_html=True)
    
    st.markdown("""
        <a class="sidebar-btn" href="https://cover.gujarathajhouse.in" target="_blank">
            📩 Cover Information
        </a>
        <a class="sidebar-btn" href="https://slip.hajsupport.com/" target="_blank">
            📄 PaySlip Generator
        </a>
        <a class="sidebar-btn" href="https://medical.hajsupport.com/" target="_blank">
            ⚕️ Medical Certificate Generator
        </a>
        <a class="sidebar-btn" href="https://stickers.hajsupport.com/" target="_blank">
            🏷️ Luggage Stickers Generator
        </a>
        <hr style="margin-top: 20px; margin-bottom: 20px; border-color: #D3D6DF;">
    """, unsafe_allow_html=True)

# Main Application Title
st.title("🕋 Haj 2027 Document Optimizer")

# --- CREATE APPLICATION TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🚀 Document Processor", 
    "📋 Scanning Guidelines", 
    "⚡ Bookmarklet Installer", 
    "🛠️ Developer Raw Script"
])

# ==========================================
# TAB 1: CORE APPLICATION WORKFLOW
# ==========================================
with tab1:
    RULES_PP = {"min_kb": 100, "max_kb": 500, "dims": (1200, 800), "label": "Passport Scanned copy"}
    RULES_PIC = {"min_kb": 5, "max_kb": 20, "dims": (480, 640), "label": "Passport Size Photograph"}
    RULES_BANK = {"min_kb": 80, "max_kb": 250, "dims": (750, 500), "label": "Bank Cheque"}

    def compress_image_to_target(img, rules):
        img_resized = img.resize(rules["dims"], Image.Resampling.LANCZOS)
        low_q, high_q = 10, 95
        best_buffer = None
        
        for _ in range(7):
            mid_q = (low_q + high_q) // 2
            buf = BytesIO()
            img_resized.save(buf, format="JPEG", optimize=True, quality=mid_q)
            size_kb = len(buf.getvalue()) / 1024
            
            if rules["min_kb"] <= size_kb <= rules["max_kb"]:
                best_buffer = buf.getvalue()
                break
            elif size_kb > rules["max_kb"]:
                high_q = mid_q - 1
            else:
                low_q = mid_q + 1
                best_buffer = buf.getvalue()
                
        if best_buffer is None:
            buf = BytesIO()
            img_resized.save(buf, format="JPEG", optimize=True, quality=low_q)
            best_buffer = buf.getvalue()
            
        return best_buffer

    uploaded_file = st.file_uploader("Upload Bulk Adobe Scan PDF", type=["pdf"])

    if uploaded_file is not None:
        raw_name = uploaded_file.name.rsplit('.', 1)[0]
        clean_name = re.sub(r'[^a-zA-Z0-9]', '-', raw_name).strip('-')
        clean_name = re.sub(r'-+', '-', clean_name)
        
        current_date = datetime.now().strftime("%d-%m-%y
