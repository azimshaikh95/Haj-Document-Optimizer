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

    st.markdown("<h2 class='sidebar-section-title'>🌐 Supportive Apps</h2>", unsafe_allow_html=True)
    
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
        
        current_date = datetime.now().strftime("%d-%m-%y")
        folder_name = f"{current_date}-{clean_name}"
        zip_filename = f"{folder_name}.zip"

        with st.spinner("Converting bulk PDF into pages..."):
            file_bytes = uploaded_file.read()
            pages = convert_from_bytes(file_bytes)
        
        total_pages = len(pages)
        st.success(f"Successfully loaded {total_pages} pages!")
        
        if total_pages >= 4 and (total_pages - 1) % 3 == 0:
            num_pilgrims = (total_pages - 1) // 3
            st.info(f"📋 **Smart Detection:** Found exactly **{num_pilgrims} pilgrim(s)** in this document group sequence.")
        else:
            num_pilgrims = max(1, round((total_pages - 1) / 3))
            st.warning(f"⚠️ **Page Count Warning:** The PDF has {total_pages} pages, which doesn't perfectly fit a standard group structure. The app is guessing **{num_pilgrims} pilgrim(s)**. Please review individual pages carefully.")

        expected_sequence = []
        for p in range(1, num_pilgrims + 1):
            expected_sequence.append({"filename": f"{p}PP1.jpg", "rules": RULES_PP, "desc": f"Pilgrim {p} Passport Page 1"})
            expected_sequence.append({"filename": f"{p}PP2.jpg", "rules": RULES_PP, "desc": f"Pilgrim {p} Passport Page 2"})

        for p in range(1, num_pilgrims + 1):
            expected_sequence.append({"filename": f"{p}PIC.jpg", "rules": RULES_PIC, "desc": f"Pilgrim {p} Photograph"})

        expected_sequence.append({"filename": "BANK.jpg", "rules": RULES_BANK, "desc": "Cover Group Bank Cheque"})

        processed_images = {}
        with st.spinner("Optimizing and compressing all files..."):
            for idx, page in enumerate(pages):
                if idx < len(expected_sequence):
                    step = expected_sequence[idx]
                    comp_bytes = compress_image_to_target(page, step["rules"])
                    processed_images[step["filename"]] = comp_bytes

        if processed_images:
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for filename, img_bytes in processed_images.items():
                    zip_file.writestr(f"{folder_name}/{filename}", img_bytes)
            
            st.markdown("### 📥 Download All Work at Once")
            
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
                </style>
            """, unsafe_allow_html=True)
            
            st.download_button(
                label=f"📦 Download All Images as ZIP ({zip_filename})",
                data=zip_buffer.getvalue(),
                file_name=zip_filename,
                mime="application/zip",
                key="big_zip_btn"
            )

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

# ==========================================
# TAB 2: GUIDELINES TAB (WITH AUTO BACKUP)
# ==========================================
with tab2:
    st.write("Review the specific scanning order required to pass validation processes automatically.")
    
    parsed_guidelines = ""
    for path in ["guidelines.md", "./guidelines.md"]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                parsed_guidelines = f.read()
            break
            
    if parsed_guidelines:
        st.markdown(parsed_guidelines)
    else:
        st.markdown("""
        ### 🕋 Scanning Rules for Volunteers

        #### 1. Before You Scan
        * **Use Color:** Set your Adobe Scan filter to **"Original Color"**. *Black & white scans/photocopies are rejected.*
        * **Clean Margins:** Place documents on a flat, dark background so the app edges crop cleanly.

        #### 2. The Golden Scanning Sequence
        Scan the entire cover group into **one single PDF file** in this exact order:
        1. **Passports First:** Cover Head Passport Page 1 → Page 2, then Co-Pilgrims Page 1 → Page 2.
        2. **Photographs Second:** Cover Head Photo → Co-Pilgrim Photos in order.
        3. **Bank Details Last:** Scan **only one** Bank Cheque for the entire family group at the very end.

        #### 3. Page Count Cheat Sheet
        * **1 Pilgrim:** 4 pages total | **2 Pilgrims:** 7 pages total | **3 Pilgrims:** 10 pages total
        """)

# ==========================================
# TAB 3: BOOKMARKLET INSTALLER TAB
# ==========================================
with tab3:
    st.markdown("### ⚡ Form Helper Bookmarklet")
    st.write("This tool speeds up data entry on the Haj portal. It completely removes page copy/paste constraints and locks, and automatically matches/re-confirms duplication inputs instantly.")
    
    # Dynamic Check for your Git-pushed 'bookmark_snippet' file
    bookmarklet_code = ""
    for path in ["bookmark_snippet", "./bookmark_snippet"]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                bookmarklet_code = f.read().strip()
            break
            
    if bookmarklet_code:
        st.code(bookmarklet_code, language="javascript")
    else:
        # Emergency local hardcoded fallback in case the Git file disappears or errors out
        fallback_bookmarklet = "javascript:(function(){const pairs={'passport_no':'c_passport_no','issue_place':'c_issue_place','issue_date':'c_issue_date','expiry_date':'c_expiry_date','birth_date':'c_birth_date','applicant_first_name':'c_applicant_first_name','applicant_last_name':'c_applicant_last_name','gender_name':'c_gender_name','birth_place':'c_birth_place','account_holder_name':'c_account_holder_name','bank_name':'c_bank_name','account_number':'c_account_number','ifsc_code':'c_ifsc_code'};const targetFields=Object.keys(pairs).reduce((acc,key)=>{acc.push(key,pairs[key]);return acc;},[]);const allDateFields=['#issue_date','#expiry_date','#birth_date','#c_issue_date','#c_expiry_date','#c_birth_date'];function unlockEverything(){targetFields.forEach(function(id){var $el=$('#'+id);if($el.length){$el.off('copy paste cut drop keydown.prevent-shortcuts contextmenu.prevent-shortcuts');$el.css({'user-select':'text','-webkit-user-select':'text','-moz-user-select':'text','-ms-user-select':'text'});}});allDateFields.forEach(function(selector){var $el=$(selector);if($el.length){$el.removeAttr('readonly').prop('readonly',false).css('background-color','#fff');if(typeof $el.datepicker==='function'){try{$el.datepicker('destroy');}catch(e){}}$el.off('keydown keypress keyup focus click change');}});}function runHcoiAutoMirrorEngine(){Object.keys(pairs).forEach(topId=>{const bottomId=pairs[topId];const topEl=document.getElementById(topId);const bottomEl=document.getElementById(bottomId);if(topEl&&bottomEl){const currentVal=topEl.value;if(currentVal&&currentVal.trim()!==""&&bottomEl.value!==currentVal){bottomEl.removeAttribute('readonly');bottomEl.readOnly=false;bottomEl.disabled=false;bottomEl.style.backgroundColor='#fff';bottomEl.value=currentVal;if(topId==='birth_date'&&typeof calculateAge==='function'){try{const calculatedAge=calculateAge(currentVal);const ageBox=document.getElementById('c_age');if(ageBox){ageBox.removeAttribute('readonly');ageBox.readOnly=false;ageBox.value=calculatedAge;$('#frmedit').bootstrapValidator('revalidateField','c_age');}}catch(e){}}try{$('#frmedit').bootstrapValidator('revalidateField',$(bottomEl).attr('name'));}catch(e){}}}});}unlockEverything();$(document).on('focus click input change keyup paste select','input, select, textarea',function(){unlockEverything();});$(document).on('blur input change keyup paste','#c_birth_date',function(){var val=$(this).val();if(val&&val.includes('-')){try{var calculatedAge=calculateAge(val);$('#c_age').val(calculatedAge);$('#frmedit').bootstrapValidator('revalidateField','c_age');}catch(e){}}try{$('#frmedit').bootstrapValidator('revalidateField',$(this).attr('name'));}catch(e){}});if(window.hcoiMirrorInterval){clearInterval(window.hcoiMirrorInterval);}window.hcoiMirrorInterval=setInterval(runHcoiAutoMirrorEngine,300);console.log(\"🛡️🚀 Ultimate Unified Engine Active via Bookmarklet!\");})();"
        st.code(fallback_bookmarklet, language="javascript")
    
    st.markdown("""
    ---
    ### 🛠️ One-Time Setup Instructions:
    1. Click the **Copy icon** in the top-right corner of the code window above.
    2. On your web browser toolbar, right-click an empty space on your **Bookmarks Bar** and click **Add Page** (or **Add Bookmark**).
    3. Enter the name as: `⚡ HCOI Form Unlocker`
    4. In the **URL / Location** box, completely delete any existing text, paste (`Ctrl+V` or `Cmd+V`) the code block you copied, and click **Save**.
    
    ### 🏃‍♂️ How to Use it:
    * Every time you open or refresh an applicant entry screen on the Haj Portal, simply click the **⚡ HCOI Form Unlocker** link button on your Bookmarks bar.
    * Type or paste data into the top main fields normally. The script will automatically mirror everything into the verification fields down the page every 300ms, updating system metrics concurrently!
    """)

# ==========================================
# TAB 4: DEVELOPER RAW SCRIPT CONFIGURATION
# ==========================================
with tab4:
    st.markdown("### 🛠️ Clear-Text Structural Automation Script")
    st.write("This tab displays the clean, un-minified developer layout of your automation script engine from your repo file.")
    
    # Dynamic check for your un-minified text config script
    clear_script_code = ""
    for path in ["script", "./script"]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                clear_script_code = f.read()
            break
            
    if clear_script_code:
        st.code(clear_script_code, language="javascript")
    else:
        # Fallback developer code block display 
        fallback_developer_text = """(function() {
    const hcoiFieldPairs = {
        'passport_no': 'c_passport_no',
        'issue_place': 'c_issue_place',
        'issue_date': 'c_issue_date',
        'expiry_date': 'c_expiry_date',
        'birth_date': 'c_birth_date',
        'applicant_first_name': 'c_applicant_first_name',
        'applicant_last_name': 'c_applicant_last_name',
        'gender_name': 'c_gender_name',
        'birth_place': 'c_birth_place',
        'account_holder_name': 'c_account_holder_name',
        'bank_name': 'c_bank_name',
        'account_number': 'c_account_number',
        'ifsc_code': 'c_ifsc_code'
    };
    // ... Module logic processes data synchronously ...
})();"""
        st.code(fallback_developer_text, language="javascript")
        
    st.markdown("""
    ---
    ### 🏃‍♂️ How to Run the Raw Script Manually:
    
    If a volunteer is having trouble with the bookmarklet or prefers using the developer options directly, they can copy and inject this code manually on every new page load:
    
    1. **Copy the Code:** Click the **Copy icon** in the top-right corner of the code block above.
    2. **Open the Haj Portal:** Navigate to the candidate registration page where you need to enter data.
    3. **Open Developer Console:** * Press **F12** (or **Ctrl + Shift + I** on Windows / **Cmd + Option + I** on Mac).
       * Click on the **Console** tab at the top of the panel that opens.
    4. **Paste and Execute:** Click inside the console line, paste the code (`Ctrl + V` or `Cmd + V`), and press **Enter**.
    5. **Close and Type:** You can close the developer panel by pressing **F12** again. Copy-paste locks are now removed, and fields will sync automatically as you type!
    """)
    
    st.info("ℹ️ This clean source text is provided for tracking updates or pushing individual components to a GitHub repository codebase.")
