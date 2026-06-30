# 🕋 Haj 2027 Document Optimizer

An automated bulk document manipulation tool designed to save processing time for volunteers handling pilgrim registrations for Haj 2027.

🚀 **Live Application URL:** [https://haj-2027.streamlit.app/](https://haj-2027.streamlit.app/)

---

## ✨ Features

* **Smart Sequence Detection:** Automatically calculates the number of pilgrims in a cover group based on the PDF page count.
* **Auto-Resizing & Compression:** Dynamically scales and compresses images to meet strict official dimensions and Kilobyte (KB) limits.
* **Standardized Naming Conventions:** Instantly names files correctly (`1PP1.jpg`, `1PP2.jpg`, `1PIC.jpg`, `BANK.jpg`) to comply with portal restrictions forbidding spaces or special characters.
* **Bulk Export:** Bundles all processed, structured images into a single, organized ZIP file appended with the extraction date.
* **Integrated Shortcuts:** Sidebar web access directly to the registration portal and login screen to streamline the data upload process.

---

## 📋 Quick Workflow for Volunteers

1. **Scan Documents:** Use Adobe Scan on your phone to capture all documents for a cover group into **one multi-page PDF** in the exact guideline sequence (Passports first, Photographs second, Bank Cheque last).
2. **Upload and Calculate:** Drag the PDF into the app. It will auto-detect the pilgrim count and show a live file conversion breakdown.
3. **Download Package:** Click the large dark button **"📦 Download All Images as ZIP"** at the top of the interface.
4. **Submit Application:** Use the portal shortcuts in the left sidebar to open the official Haj panels and upload the freshly organized imagery.
