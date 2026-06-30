import streamlit as st
from pdf2image import convert_from_bytes
from PIL import Image
from io import BytesIO

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
        
    return best_buffer, len(best_buffer) / 1024

# 1. Ask how many pilgrims are in this cover group
num_pilgrims = st.number_input("How many pilgrims are in this scan?", min_value=1, max_value=5, value=2, step=1)

# 2. Dynamically build the expected sequence mapping
expected_sequence = []

# First: All Passports (PP1 then PP2 for each pilgrim)
for p in range(1, num_pilgrims + 1):
    expected_sequence.append({"filename": f"{p}PP1.jpg", "rules": RULES_PP, "desc": f"Pilgrim {p} Passport Page 1"})
    expected_sequence.append({"filename": f"{p}PP2.jpg", "rules": RULES_PP, "desc": f"Pilgrim {p} Passport Page 2"})

# Second: All Photographs
for p in range(1, num_pilgrims + 1):
    expected_sequence.append({"filename": f"{p}PIC.jpg", "rules": RULES_PIC, "desc": f"Pilgrim {p} Photograph"})

# Third: The single Bank Cheque for the entire cover group
expected_sequence.append({"filename": "1BANK.jpg", "rules": RULES_BANK, "desc": "Cover Group Bank Cheque"})

total_expected_pages = len(expected_sequence)

st.info(f"📋 For **{num_pilgrims} pilgrims**, the app expects a **{total_expected_pages}-page PDF** in your exact scan order.")

# File Upload UI
uploaded_file = st.file_uploader("Upload Bulk Adobe Scan PDF", type=["pdf"])

if uploaded_file is not None:
    with st.spinner("Converting bulk PDF into pages..."):
        file_bytes = uploaded_file.read()
        pages = convert_from_bytes(file_bytes)
    
    total_pages = len(pages)
    st.success(f"Successfully loaded {total_pages} pages!")
    
    if total_pages != total_expected_pages:
        st.error(f"⚠️ Page count mismatch! The PDF has {total_pages} pages, but based on your selection, we expected exactly {total_expected_pages} pages. Please check if a page was skipped or extra pages were scanned.")

    # Process pages up to the available count
    for idx, page in enumerate(pages):
        if idx >= len(expected_sequence):
            st.warning(f"⚠️ Page {idx + 1} is extra and exceeds the configured pilgrim sequence rules.")
            continue
            
        step = expected_sequence[idx]
        filename = step["filename"]
        rules = step["rules"]
        
        st.markdown(f"---")
        st.subheader(f"📄 Page {idx + 1}: {step['desc']} ──► `{filename}`")
        st.caption(f"Document Category: **{rules['label']}**")
        
        # Process and compress
        comp_bytes, comp_size = compress_image_to_target(page, rules)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(page, use_container_width=True)
        with col2:
            st.success(f"⚡ Compressed size: **{comp_size:.2f} KB**")
            st.caption(f"Allowed: {rules['min_kb']}-{rules['max_kb']} KB | Dimensions: {rules['dims'][0]}x{rules['dims'][1]}px")
            
            # Download button with automated custom filename
            st.download_button(
                label=f"⬇️ Download {filename}",
                data=comp_bytes,
                file_name=filename,
                mime="image/jpeg",
                key=f"btn_{idx}"
            )
