# --- SIDEBAR SHORTCUTS (MATCHING NATIVE UPLOAD BUTTON STYLE) ---
with st.sidebar:
    st.markdown("## 🌐 Official Portals")
    st.write("Click below to open pages in a new tab:")
    
    # Updated CSS to match the crisp native upload button style
    st.markdown("""
        <style>
            .sidebar-btn {
                display: block !important;
                text-align: center !important;
                background-color: #FFFFFF !important;    /* Crisp white background */
                color: #262730 !important;              /* Dark text for perfect readability */
                border: 1px solid #D3D6DF !important;    /* Soft gray border matching the Upload button */
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
                background-color: #F8F9FA !important;    /* Subtle light gray shift on hover */
                border-color: #A3A8B8 !important;        /* Darker border on hover */
                color: #262730 !important;
                text-decoration: none !important;
            }
        </style>
        
        <a class="sidebar-btn" href="https://hajcommittee.gov.in/registration" target="_blank">
            📝 Registration Form
        </a>
        <a class="sidebar-btn" href="https://hajcommittee.gov.in/login" target="_blank">
            🔑 Login Page
        </a>
        <hr style="margin-top: 20px; margin-bottom: 20px; border-color: #D3D6DF;">
    """, unsafe_allow_html=True)
