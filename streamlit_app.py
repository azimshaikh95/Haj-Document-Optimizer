# ZIP Download All Button placed at the top
    if processed_images:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for filename, img_bytes in processed_images.items():
                zip_file.writestr(f"{folder_name}/{filename}", img_bytes)
        
        # CHANGED: Reverted header back to native left-alignment
        st.markdown("### 📥 Download All Work at Once")
        
        # Inject Custom CSS to cleanly style the full-width button
        st.markdown("""
            <style>
                /* Style the button to match the dark aesthetic and fill the width naturally */
                div.stDownloadButton > button {
                    background-color: #1E1E1E !important;
                    color: #FFFFFF !important;
                    border: 2px solid #333333 !important;
                    padding: 15px 25px !important;
                    font-size: 18px !important;
                    font-weight: bold !important;
                    border-radius: 8px !important;
                    width: 100% !important; /* Spans across matching the upload boxes */
                    transition: all 0.3s ease !important;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
                }
                
                /* Micro-interactions */
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
