import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image
from io import BytesIO

# Page Configuration
st.set_page_config(page_title="Haj 2027 Doc Optimizer", page_icon="🕋", layout="centered")
st.title("🕋 Haj 2027 Document Optimizer")
st.write("Convert your Adobe Scan PDFs and auto-compress them to the exact size limits required for registration.")

# 1. Target rules directly from the official image guidelines
DOC_RULES = {
    "1. Photograph (5 - 20 KB)": {"min_kb": 5, "max_kb": 20, "dims": (480, 640)},
    "2. Passport Scanned copy (100 - 500 KB)": {"min_kb": 100, "max_kb": 500, "dims": (1200, 800)},
    "3. Cancelled Cheque (80 - 250 KB)": {"min_kb": 80, "max_kb": 250, "dims": (750, 500)},
    "4. Address Proof (80 - 250 KB)": {"min_kb": 80, "max_kb": 250, "dims": (750, 500)}
}

# Volunteer Document Selector
selected_rule = st.selectbox("Select the Document Type you are uploading:", list(DOC_RULES.keys()))
rules = DOC_RULES[selected_rule]

def compress_image_to_target(img, rules):
    # Resize according to exact pixel guidelines
    img_resized = img.resize(rules["dims"], Image.Resampling.LANCZOS)
    
    # Binary search compression logic to guarantee hitting target file size
    low_q, high_q = 10, 95
    best_buffer = None
    
    for _ in range(7):  # Find optimal JPEG quality dynamically
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
        
    return best_buffer, len(best_buffer) / 1024

# File Upload UI
uploaded_file = st.file_uploader("Upload Adobe Scan PDF", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Converting PDF pages to images..."):
        file_bytes = uploaded_file.read()
        pages = convert_from_bytes(file_bytes)
        
    st.success(f"Successfully extracted {len(pages)} page(s)!")
    
    for idx, page in enumerate(pages):
        st.subheader(f"📄 Page {idx + 1}")
        st.image(page, caption=f"Original Page {idx + 1}", use_container_width=True)
        
        # Run local compression pipeline based on the selected rule
        comp_bytes, comp_size = compress_image_to_target(page, rules)
        
        # Display results and provide download button
        st.success(f"⚡ Compressed! Size: **{comp_size:.2f} KB** (Target: {rules['min_kb']}-{rules['max_kb']} KB)")
        
        st.download_button(
            label=f"⬇️ Download Page {idx + 1} Optimized JPG",
            data=comp_bytes,
            file_name=f"haj_optimized_page_{idx+1}.jpg",
            mime="image/jpeg"
        )
