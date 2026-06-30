import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image
from io import BytesIO
import zipfile
import re
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Haj Dynamic Doc Optimizer", page_icon="🕋", layout="centered")
st.title("🕋 Haj 2027 Bulk Document Optimizer")
st.write("Configure the number of pilgrims, upload the PDF, and download perfectly named, compliant files.")

# Rule Configurations
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

# 1. Ask how many pilgrims are in this cover group
num_pilgrims = st.number_input("How many pilgrims are in this scan?", min_value=1, max_value=5, value=2, step=1)

# 2. Dynamically build the expected sequence mapping based on your exact scanning order
expected_sequence = []
for p in range(1, num_pilgrims + 1):
    expected_sequence.append({"filename": f"{p}PP1.jpg", "rules": RULES_PP, "desc": f"Pilgrim {p} Passport Page 1"})
    expected_sequence.append({"filename": f"{p}PP2.jpg", "rules": RULES_PP, "desc": f"Pilgrim {p} Passport Page 2"})

for p in range(1, num_pilgrims + 1):
    expected_sequence.append({"filename": f"{p}PIC.jpg", "rules": RULES_PIC, "desc": f"Pilgrim {p} Photograph"})

expected_sequence.append({"filename": "BANK.jpg", "rules": RULES_BANK, "desc": "Cover Group Bank Cheque"})

total_expected_pages = len(expected_sequence)
st.info(f"📋 For **{num_pilgrims} pilgrims**, the app expects a **{total_expected_pages}-page PDF** in your exact scan order.")

# File Upload UI
uploaded_file = st.file_uploader("Upload Bulk Adobe Scan PDF", type=["pdf"])

if uploaded_file is not None:
    # Extract the clean file name without extension
    raw_name = uploaded_file.name.rsplit('.', 1)[0]
    clean_name = re.sub(r'[^a-zA-Z0-9]', '-', raw_name).strip('-')
    clean_name = re.sub(r'-+', '-', clean_name)
    
    # Generate Folder & ZIP name
    current_date = datetime.now().strftime("%d-%m-%y")
    folder_name = f"{current_date}-{clean_name}"
    zip_filename = f"{folder_name}.zip"

    with st.spinner("Converting bulk PDF into pages..."):
        file_bytes = uploaded_file.read()
        pages = convert_from_bytes(file_bytes)
    
    total_pages = len(pages)
    st.success(f"Successfully loaded {total_pages} pages!")
    
    if total_pages != total_expected_pages:
        st.error(f"⚠️ Page count mismatch! The PDF has {total_pages} pages, but we expected exactly {total_expected_pages}. Please check if a page was skipped.")

    # Pre-process and compress all images into a dictionary for the ZIP archive
    processed_images = {}
    with st.spinner("Optimizing and compressing all files..."):
        for idx, page in enumerate(pages):
            if idx < len(expected_sequence):
                step = expected_sequence[idx]
                comp_bytes = compress_image_to_target(page, step["rules"])
                processed_images[step["filename"]] = comp_bytes

    # ZIP Download All Button placed at the top
    if processed_images:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for filename, img_bytes in processed_images.items():
                zip_file.writestr(f"{folder_name}/{filename}", img_bytes)
        
        # Centered Header text
        st.markdown("<h3 style='text-align: center;'>📥 Download All Work at Once</h3>", unsafe_allow_html=True)
        
        # Inject Custom CSS to forcefully center the container, row, and inner button element
        st.markdown("""
            <style>
                /* Target the element wrapper directly to align its inner components to center */
                .element-container:has(iframe), 
                .element-container:has(button#big_zip_btn),
                div.stDownloadButton {
                    display: flex !important;
                    justify-content: center !important;
                    align-items: center !important;
                    width: 100% !important;
                    text-align: center !important;
                }
                
                /* Force alignment on the data block container */
                div.stDownloadButton > data {
                    display: flex !important;
                    justify-content: center !important;
                    width: 100% !important;
                }
                
                /* Target the download button layout attributes */
                div.stDownloadButton button {
                    background-color: #1E1E1E !important;
                    color: #FFFFFF !important;
                    border: 2px solid #333333 !important;
                    padding: 15px 35px !important;
                    font-size: 20px !important;
                    font-weight: bold !important;
                    border-radius: 8px !important;
                    width: auto !important;
                    min-width: 340px !important;
                    margin: 0 auto !important; /* Forces block margins to split equally left and right */
                    transition: all 0.3s ease !important;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
                    display: inline-flex !important;
                    justify-content: center !important;
                    align-items: center !important;
                }
                
                /* Hover styling interactions */
                div.stDownloadButton button:hover {
                    background-color: #333333 !important;
                    border-color: #4F4F4F !important;
                    transform: translateY(-2px) !important;
                    box-shadow: 0 6px 8px rgba(0,0,0,0.3) !important;
                }
                div.stDownloadButton button:active {
                    transform: translateY(1px) !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        st.download_button(
            label=f"📦 Download All Images as ZIP ({zip_filename})",
            data=zip_buffer.getvalue(),
            file_name=zip_filename,
            mime="application/zip",
            key="big_zip_btn
