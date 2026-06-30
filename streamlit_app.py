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

    # ZIP Download All Button placed at the top (FIXED INDENTATION)
    if processed_images:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for filename, img_bytes in processed_images.items():
                zip_file.writestr(f"{folder_name}/{filename}", img_bytes)
        
        st.markdown("### 📥 Download All Work at Once")
        
        # Inject Custom CSS to style the big download button
        st.markdown("""
            <style>
                div.stDownloadButton > button {
                    background-color: #1E1E1E !important;
                    color: #FFFFFF !important;
                    border: 2px solid #333333 !important;
                    padding: 15px 25px !important;
                    font-size: 20px !important;
                    font-weight: bold !important;
                    border-radius: 8px !important;
                    width: 100% !important;
                    transition: all 0.3s ease !important;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.2) !important;
                }
                div.stDownloadButton > button:hover {
                    background-color: #333333 !important;
                    border-color: #4F4F4F !important;
                    transform: translateY(-2px) !important;
                    box-shadow: 0 6px 8px rgba(0,0,0,0.3) !important;
                }
                div.stDownloadButton > button:active {
                    transform: translateY(1px) !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        st.download_button(
            label=f"📦 DOWNLOAD ALL IMAGES AS ZIP ({zip_filename})",
            data=zip_buffer.getvalue(),
            file_name=zip_filename,
            mime="application/zip",
            key="big_zip_btn"
        )
