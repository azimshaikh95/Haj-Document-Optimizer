import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image
from io import BytesIO
import zipfile
import re
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Haj Auto Doc Optimizer", page_icon="🕋", layout="centered")
st.title("🕋 Haj 2027 Bulk Document Optimizer")
st.write("Upload your bulk Adobe Scan PDF. The app will automatically detect the number of pilgrims and process everything.")

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
    
    # AUTOMATED PREDICTION MATH
    # Calculate pilgrims based on: (Total Pages - 1 Cheque) / 3 documents per pilgrim
    if total_pages >= 4 and (total_pages - 1) % 3 == 0:
        num_pilgrims = (total_pages - 1) // 3
        st.info(f"📋 **Smart Detection:** Found exactly **{num_pilgrims} pilgrim(s)** in this document group sequence.")
    else:
        # Fallback math calculation if the scanner missed a page or added extra pages
        num_pilgrims = max(1, round((total_pages - 1) / 3))
        st.warning(f"⚠️ **Page Count Warning:** The PDF has {total_pages} pages, which doesn't perfectly fit a standard group structure. The app is guessing **{num_pilgrims} pilgrim(s)**. Please review individual pages carefully.")

    # Dynamically build the expected sequence mapping based on your exact scanning order
    expected_sequence = []
    for p in range(1, num_pilgrims + 1):
        expected_sequence.append({"filename": f"{p}PP1.jpg", "rules": RULES_PP, "desc": f"Pilgrim {p} Passport Page 1"})
        expected_sequence.append({"filename": f"{p}PP2.jpg", "rules": RULES_PP, "desc": f"Pilgrim {p} Passport Page 2"})

    for p in range(1, num_pilgrims + 1):
        expected_sequence.append({"filename": f"{p}PIC.jpg", "rules": RULES_PIC, "desc": f"Pilgrim {p} Photograph"})

    expected_sequence.append({"filename": "BANK.jpg", "rules": RULES_BANK, "desc": "Cover Group Bank Cheque"})

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
        
        st.markdown("### 📥 Download All Work at Once")
        
        # Inject Custom CSS to cleanly style the full-width button
        st.markdown("""
            <style>
                div.stDownloadButton > button {
                    background-color: #1E1E1E !important;
                    color: #FFFFFF !important;
                    border: 2px solid #333333 !important;
                    padding: 15px 25px !important;
                    font-size: 18px !important;
                    font-weight: bold !important;
                    border-radius: 8px !important;
                    width: 100% !important;
                    transition: all 0.3s ease !important;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
                }
                div.stDownloadButton > button:hover {
                    background-color: #333333 !important;
                    border-color: #4F4F4F !important;
                }
                div.stDownloadButton > button:active {
                    transform: translateY(1px) !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        st.download_button(
            label=f"📦 Download All Images as ZIP ({zip_filename})",
            data=zip_buffer.getvalue(),
            file_name=zip_filename,
            mime="application/zip",
            key="big_zip_btn"
        )

    # Process individual pages display lower down for manual review
    for idx, page in enumerate(pages):
        if idx >= len(expected_sequence):
            st.warning(f"⚠️ Page {idx + 1} is extra and exceeds predicted sequence boundaries.")
            continue
            
        step = expected_sequence[idx]
        filename = step["filename"]
        rules = step["rules"]
        
        st.markdown(f"---")
        st.subheader(f"📄 Page {idx + 1}: {step['desc']} ──► `{filename}`")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(page, use_container_width=True)
        with col2:
            if filename in processed_images:
                size_kb = len(processed_images[filename]) / 1024
                st.success(f"⚡ Compressed size: **{size_kb:.2f} KB**")
            st.caption(f"Allowed: {rules['min_kb']}-{rules['max_kb']} KB | Dimensions: {rules['dims'][0]}x{rules['dims'][1]}px")
            
            if filename in processed_images:
                st.download_button(
                    label=f"⬇️ Download {filename} Individually",
                    data=processed_images[filename],
                    file_name=filename,
                    mime="image/jpeg",
                    key=f"btn_{idx}"
                )
