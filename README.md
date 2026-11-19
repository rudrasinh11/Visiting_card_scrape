# Visiting Card Scanner & Contact Manager (Red & White Minimal Edition)

A 100% free, offline, zero-API-cost visiting card scanner web app built with **Streamlit** and **RapidOCR (ONNX)**.

Everything runs locally on your machine with **no cloud dependencies, no API keys, and no subscriptions**.

---

## Features
- **Minimal Red & White UI**: Clean, high-contrast, distraction-free aesthetic with custom styling.
- **Dual Input Methods**:
  - Upload image files (PNG, JPG, JPEG, WEBP).
  - Snap live card photos directly with your laptop webcam.
- **Automatic Field Extraction**:
  - Name & Designation (CEO, Director, Manager, Founder, Doctor, etc.)
  - Company / Organization Name
  - Phone Numbers (+91, international, mobile, and landlines)
  - Email Addresses
  - Websites
  - Postal PIN / Zip Codes
  - GSTIN (15-digit Indian Tax ID)
  - Address / Raw Text
- **Interactive Review & Verification**: Review and adjust any field before saving to the database.
- **Data Table & Exports**:
  - Inline editing of saved records directly inside the browser.
  - Export to **Excel (`.xlsx`)** with one click.
  - Export to **CSV** format anytime.
- **Privacy & Zero Cost**:
  - Fully local: Your contacts are never sent over the internet.
  - Zero API charges: No OpenAI, Google Cloud, or AWS bills.

---

## How to Run

### Method 1: One-Click Batch File
Double-click `run_app.bat` inside `E:\visiting-card-scanner\`.

### Method 2: Command Line (PowerShell / Terminal)
```powershell
cd E:\visiting-card-scanner
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## Project Structure (All in Drive E)
```
E:\visiting-card-scanner\
├── .streamlit\
│   └── config.toml        # Red & White minimal theme configuration
├── app.py                 # Main Streamlit application
├── contacts.csv           # Local CSV database of extracted cards
├── run_app.bat            # 1-click launcher script
├── test_pipeline.py       # Offline verification test
├── sample_card.png        # Generated test business card
└── README.md              # Project documentation
```
