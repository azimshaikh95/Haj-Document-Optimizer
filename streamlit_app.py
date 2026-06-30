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

expected_sequence.append({"filename": "1BANK.jpg", "rules": RULES_BANK, "desc": "Cover Group Bank Cheque"})

total_expected_pages = len(expected_sequence)
st.info(f"📋 For **{num_pilgrims} pilgrims**, the app expects a **{total_expected_pages}-page PDF** in your exact scan order.")

# File Upload UI
uploaded_file = st.file_uploader("Upload Bulk Adobe Scan PDF", type=["pdf"])

if uploaded_file is not None:
    # Extract the clean file name without extension
    raw_name = uploaded_file.name.rsplit('.', 1)[0]
    # Replace spaces and special characters with hyphens to comply with Haj site rules
    clean_name = re.sub(r'[^a-zA-Z0-9]', '-', raw_name).strip('-')
    # Remove any double hyphens
    clean_name = re.sub(r'-+', '-', clean_name)
    
    # Generate Folder & ZIP name matching "30-6-26-Iqbal-Bhai"
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
                # Store the file mapping into our structure
                processed_images[step["filename"]] = comp_bytes

    # --- NEW: ZIP Download All Button placed at the top ---
    if processed_images:
        # Create ZIP completely in-memory
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for filename, img_bytes in processed_images.items():
                # Placing them directly inside a folder inside the ZIP file structure
                zip_file.writestr(f"{folder_name}/{filename}", img_bytes)
        
        st.markdown("### 📥 Download All Work at Once")
        st.download_button(
            label=f"💥 Download All Images as ZIP (`{zip_filename}`)",
            data=zip_buffer.getvalue(),
            file_name=zip_filename,
            mime="application/zip",
            use_container_width=True
        )

    # Process individual pages display lower down for manual review
    for idx, page in enumerate(pages):
        if idx >= len(expected_sequence):
            st.warning(f"⚠️ Page {idx + 1} is extra and exceeds configured sequence rules.")
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
            
            # Individual fallbacks just in case
            if filename in processed_images:
                st.download_button(
                    label=f"⬇️ Download {filename} Individually",
                    data=processed_images[filename],
                    file_name=filename,
                    mime="image/jpeg",
                    key=f"btn_{idx}"
                )
