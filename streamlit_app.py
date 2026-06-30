# ZIP Download All Button placed at the top
if processed_images:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for filename, img_bytes in processed_images.items():
                zip_file.writestr(f"{folder_name}/{filename}", img_bytes)
        
        st.markdown("### 📥 Download All Work at Once")
        
        # Inject Custom CSS to style the big download button
        st.markdown("""
            <style>
                /* Target the specific download button using Streamlit's button container element */
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
                /* Add a nice hover effect so volunteers know it's interactive */
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
        
        # Updated symbol to a solid file-zip/package icon (📁/📦) and enhanced size layout
        st.download_button(
            label=f"📦 DOWNLOAD ALL IMAGES AS ZIP ({zip_filename})",
            data=zip_buffer.getvalue(),
            file_name=zip_filename,
            mime="application/zip",
            key="big_zip_btn"
        )
