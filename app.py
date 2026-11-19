import os
import re
import hashlib
from io import BytesIO
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st
from rapidocr_onnxruntime import RapidOCR

# --- Page Configuration ---
st.set_page_config(
    page_title="CardScan // Minimal Red & White",
    page_icon="📇",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- Cloud & Local Production-Ready Path Management ---
BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = Path(os.getenv("CONTACTS_STORAGE_PATH", BASE_DIR / "contacts.csv"))
COLUMNS = ["Name", "Designation", "Company", "Phone", "Email", "Website", "Address"]

# --- Minimalist Red & White CSS (Strict 2-Color Palette) ---
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap');

        /* Global Reset */
        html, body, [class*="css"], .stApp {
            font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
            background-color: #FFFFFF !important;
            color: #171717 !important;
        }

        /* Top Header */
        .app-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #DC2626;
            padding: 14px 0 16px 0;
            margin-bottom: 22px;
        }
        .app-title {
            font-size: 26px;
            font-weight: 700;
            letter-spacing: -0.5px;
            color: #DC2626;
            margin: 0;
            text-transform: uppercase;
        }
        .app-subtitle {
            font-size: 11px;
            color: #737373;
            letter-spacing: 0.6px;
            margin-top: 3px;
            text-transform: uppercase;
            font-weight: 500;
        }
        .status-badge {
            background-color: #DC2626;
            color: #FFFFFF !important;
            padding: 5px 12px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
            border-radius: 2px;
            text-transform: uppercase;
        }

        /* Minimal Card Container */
        .stat-card {
            background: #FFFFFF;
            border: 1px solid #E5E5E5;
            border-top: 3px solid #DC2626;
            padding: 14px 18px;
            border-radius: 2px;
            text-align: left;
        }
        .stat-val {
            font-size: 26px;
            font-weight: 700;
            color: #DC2626;
            margin: 0;
            line-height: 1.1;
        }
        .stat-lbl {
            font-size: 10px;
            font-weight: 600;
            color: #737373;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin: 4px 0 0 0;
        }

        /* Section Headings */
        .section-tag {
            font-size: 13px;
            font-weight: 700;
            color: #DC2626;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* Custom Buttons */
        div.stButton > button {
            background-color: #DC2626 !important;
            color: #FFFFFF !important;
            border: 1px solid #DC2626 !important;
            border-radius: 2px !important;
            font-weight: 600 !important;
            font-size: 12px !important;
            letter-spacing: 0.5px !important;
            text-transform: uppercase !important;
            padding: 7px 16px !important;
            transition: all 0.15s ease-in-out;
        }
        div.stButton > button:hover {
            background-color: #B91C1C !important;
            border-color: #B91C1C !important;
            color: #FFFFFF !important;
            box-shadow: 0 2px 6px rgba(220, 38, 38, 0.25);
        }

        /* Secondary / Rotate Buttons */
        .rotate-btn > div.stButton > button {
            background-color: #FFFFFF !important;
            color: #DC2626 !important;
            border: 1px solid #DC2626 !important;
        }
        .rotate-btn > div.stButton > button:hover {
            background-color: #DC2626 !important;
            color: #FFFFFF !important;
        }

        /* Download Buttons */
        div.stDownloadButton > button {
            background-color: #FFFFFF !important;
            color: #DC2626 !important;
            border: 1.5px solid #DC2626 !important;
            border-radius: 2px !important;
            font-weight: 600 !important;
            font-size: 12px !important;
            text-transform: uppercase !important;
            padding: 6px 14px !important;
        }
        div.stDownloadButton > button:hover {
            background-color: #DC2626 !important;
            color: #FFFFFF !important;
        }

        /* Inputs */
        div[data-baseweb="input"], div[data-baseweb="textarea"] {
            border: 1px solid #D4D4D4 !important;
            border-radius: 2px !important;
            background-color: #FFFFFF !important;
        }
        div[data-baseweb="input"]:focus-within, div[data-baseweb="textarea"]:focus-within {
            border-color: #DC2626 !important;
            box-shadow: 0 0 0 1px #DC2626 !important;
        }

        /* Radio & Checkbox */
        div[role="radiogroup"] label {
            font-size: 12px !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
        }

        /* Custom Box */
        .empty-placeholder {
            border: 1.5px dashed #E5E5E5;
            background-color: #FAFAFA;
            padding: 40px 20px;
            text-align: center;
            border-radius: 2px;
            color: #737373;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- OCR Engine Initialization ---
@st.cache_resource
def get_ocr_engine():
    return RapidOCR()

ocr = get_ocr_engine()

@st.cache_data(show_spinner=False)
def run_ocr_on_bytes(image_bytes):
    """Cached OCR call so UI reruns (edits, clicks) are instantaneous."""
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    result, _ = ocr(np.array(img))
    return result

# --- Smart Parser Dictionaries & Rules ---
JOB_TITLES = [
    "cmd", "md", "ceo", "cto", "cfo", "coo", "cmo", "co-founder", "cofounder",
    "founder", "chairman", "managing director", "director", "general manager",
    "manager", "president", "vice president", "vp", "lead", "head", "partner",
    "associate", "executive", "officer", "principal", "consultant", "advisor",
    "architect", "engineer", "specialist", "advocate", "lawyer", "dr.", "doctor",
    "proprietor", "prop.", "promoter", "owner"
]

COMPANY_INDICATORS = re.compile(
    r"\b(pvt|ltd|limited|corp|corporation|inc|llc|enterprises|solutions|technologies|tech|studio|agency|services|consultancy|associates|industries|group|jewel|holdings|infotech)\b",
    re.I,
)

ADDRESS_KEYWORDS = re.compile(
    r"\b(road|street|nagar|plot|floor|avenue|cross|phase|opp|behind|near|building|complex|chowk|marg|bazaar|dist|state|tower|office|branch|h\.o\.|r\.o\.|indore|m\.p\.|delhi|mumbai|bangalore|ahmedabad|gujarat|pincode|\b\d{6}\b)\b",
    re.I,
)

LABEL_STRIP = re.compile(
    r"^(email|e-mail|mail|web|website|site|phone|tel|mobile|mob|cell|ph|fax|contact|office|add|address|text)\s*[:.-]\s*",
    re.I,
)

WEB_PATTERN = re.compile(
    r"(?:https?://[^\s]+|www\.[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?|\b[a-zA-Z0-9-]+\.(com|in|org|net|io|tech|co|ai|biz|info|store|app|dev)(?:/[^\s]*)?\b)",
    re.I,
)

def parse_card_elements(ocr_results):
    """
    State-of-the-art parser with cross-referencing:
    - Email username correlates to Person Name
    - Email domain correlates to Company Name
    - Strips fake websites (like pvt.ltd)
    - Collects multi-line address
    """
    if not ocr_results:
        return {}

    raw_lines = [item[1].strip() for item in ocr_results if item[1].strip()]
    full_text = "\n".join(raw_lines)

    # 1. Email Extraction
    email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", full_text)
    email = email_match.group(0).lower() if email_match else ""
    email_user = email.split("@")[0].lower() if email else ""
    email_domain = email.split("@")[1].split(".")[0].lower() if email and "@" in email else ""

    # 2. Website Extraction (Strict TLD & non-company check)
    website = ""
    for line in raw_lines:
        if "@" in line:
            continue
        # Ignore company suffix misdetected as website
        if re.search(r"\b(pvt|ltd|corp|inc|co)\.(ltd|in|com)?\b", line, re.I):
            continue
        cleaned = LABEL_STRIP.sub("", line).strip()
        m = WEB_PATTERN.search(cleaned)
        if m:
            val = m.group(0).lower().rstrip(".:,;")
            if not re.search(r"\b(pvt|corp|co)\.ltd\b", val):
                website = val
                break

    # 3. Phone Numbers
    phones = []
    for line in raw_lines:
        found_phones = re.findall(r"(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{2,5}\)?[\s.-]?)?\d{3,5}[\s.-]?\d{4,5}", line)
        for p in found_phones:
            digits = re.sub(r"\D", "", p)
            if 8 <= len(digits) <= 13 and p.strip() not in phones:
                phones.append(p.strip())
    phone_str = ", ".join(phones)

    # 4. Designation Detection
    designation = ""
    for line in raw_lines:
        cleaned = LABEL_STRIP.sub("", line).strip()
        cleaned_lower = cleaned.lower()
        if any(re.search(r"\b" + re.escape(jt) + r"\b", cleaned_lower) for jt in JOB_TITLES):
            designation = cleaned
            break

    # 5. Full Address Extraction (Combines address fragments & PIN codes)
    address_lines = []
    for line in raw_lines:
        cleaned = LABEL_STRIP.sub("", line).strip()
        if not cleaned:
            continue
        if email and email in cleaned.lower():
            continue
        if website and website in cleaned.lower():
            continue
        if any(p in cleaned for p in phones):
            continue
        if cleaned == designation:
            continue
        if re.match(r"^(email|mobile|phone|text|office|fax|cell)$", cleaned, re.I):
            continue

        if ADDRESS_KEYWORDS.search(cleaned):
            if re.match(r"^office$", cleaned, re.I):
                continue
            address_lines.append(cleaned)

    # Sort address: street/nagar first, state/pincode at the end
    clean_address = ", ".join(address_lines)

    # 6. Name and Company Identification
    candidates = []
    for line in raw_lines:
        cleaned = LABEL_STRIP.sub("", line).strip()
        if not cleaned:
            continue
        if email and email in cleaned.lower():
            continue
        if website and website in cleaned.lower():
            continue
        if any(p in cleaned for p in phones):
            continue
        if cleaned == designation:
            continue
        if cleaned in address_lines:
            continue
        if re.match(r"^(email|mobile|phone|text|office|fax|tagline|website)$", cleaned, re.I):
            continue
        # Skip small slogans like "making precious digital"
        if len(cleaned.split()) > 3 and not COMPANY_INDICATORS.search(cleaned):
            continue
        candidates.append(cleaned)

    name = ""
    company = ""

    # Smart Matching A: Check against email username -> Name
    if email_user and len(email_user) >= 3:
        user_parts = [p for p in re.split(r"[._]", email_user) if len(p) >= 3]
        for cand in candidates:
            cand_norm = re.sub(r"[^a-zA-Z0-9]", "", cand).lower()
            if any(p in cand_norm for p in user_parts):
                name = cand
                break

    # Smart Matching B: Check against email domain or company keywords -> Company
    for cand in candidates:
        if cand == name:
            continue
        cand_norm = re.sub(r"[^a-zA-Z0-9]", "", cand).lower()
        if (email_domain and email_domain in cand_norm) or COMPANY_INDICATORS.search(cand):
            company = cand
            break

    # Fallbacks if email cross-check was not available
    rem = [c for c in candidates if c not in (name, company)]
    if not name and rem:
        name = rem.pop(0)
    if not company and rem:
        company = rem.pop(0)

    return {
        "Name": name,
        "Designation": designation,
        "Company": company,
        "Phone": phone_str,
        "Email": email,
        "Website": website,
        "Address": clean_address,
    }

# --- Database Management ---
def load_contacts():
    if CSV_FILE.exists():
        try:
            df = pd.read_csv(CSV_FILE).fillna("")
            # Handle legacy CSV schema upgrade
            if "Address" not in df.columns and "Address / Raw Text" in df.columns:
                df["Address"] = df["Address / Raw Text"]
            for col in COLUMNS:
                if col not in df.columns:
                    df[col] = ""
            return df[COLUMNS]
        except Exception:
            return pd.DataFrame(columns=COLUMNS)
    return pd.DataFrame(columns=COLUMNS)

def save_contacts(df):
    df.to_csv(CSV_FILE, index=False)

def to_excel_bytes(df):
    out = BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Contacts")
    return out.getvalue()

# --- Top Header ---
st.markdown(
    """
    <div class="app-header">
        <div>
            <h1 class="app-title">Visiting Card Scanner</h1>
            <p class="app-subtitle">Zero API Cost • RapidOCR ONNX • Deploy-Ready</p>
        </div>
        <div class="status-badge">Minimal Red & White</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Statistics Bar ---
contacts_df = load_contacts()
col_s1, col_s2, col_s3, col_s4 = st.columns(4)
with col_s1:
    st.markdown(f'<div class="stat-card"><p class="stat-val">{len(contacts_df)}</p><p class="stat-lbl">Saved Cards</p></div>', unsafe_allow_html=True)
with col_s2:
    emails_cnt = len([e for e in contacts_df.get("Email", []) if str(e).strip()])
    st.markdown(f'<div class="stat-card"><p class="stat-val">{emails_cnt}</p><p class="stat-lbl">Valid Emails</p></div>', unsafe_allow_html=True)
with col_s3:
    phones_cnt = len([p for p in contacts_df.get("Phone", []) if str(p).strip()])
    st.markdown(f'<div class="stat-card"><p class="stat-val">{phones_cnt}</p><p class="stat-lbl">Phone Numbers</p></div>', unsafe_allow_html=True)
with col_s4:
    addr_cnt = len([a for a in contacts_df.get("Address", []) if str(a).strip()])
    st.markdown(f'<div class="stat-card"><p class="stat-val">{addr_cnt}</p><p class="stat-lbl">Addresses Captured</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Main Columns ---
col_scan, col_review = st.columns([1, 1], gap="large")

with col_scan:
    st.markdown('<div class="section-tag">▸ 01. CAPTURE / UPLOAD CARD</div>', unsafe_allow_html=True)
    mode = st.radio("Input Mode", ["Upload Card File", "Camera Snapshot"], horizontal=True, label_visibility="collapsed")

    raw_upload = None
    if mode == "Upload Card File":
        raw_upload = st.file_uploader(
            "Select visiting card image",
            type=["jpg", "jpeg", "png", "webp"],
            help="High-contrast, well-lit photos give the highest accuracy.",
        )
    else:
        raw_upload = st.camera_input("Point camera at visiting card")

    extracted_data = None

    if raw_upload is not None:
        raw_bytes = raw_upload.getvalue()
        file_hash = hashlib.md5(raw_bytes).hexdigest()

        # Track rotation angle in session state
        if "rotation_angle" not in st.session_state or st.session_state.get("current_file_hash") != file_hash:
            st.session_state["rotation_angle"] = 0
            st.session_state["current_file_hash"] = file_hash

        # Load & rotate image
        pil_img = Image.open(BytesIO(raw_bytes)).convert("RGB")
        if st.session_state["rotation_angle"] != 0:
            pil_img = pil_img.rotate(st.session_state["rotation_angle"], expand=True)

        st.image(pil_img, caption="Visiting Card", use_container_width=True)

        # Quick Rotation Controls (especially helpful for phone camera photos)
        rot_col1, rot_col2, rot_col3 = st.columns([1, 1, 2])
        with rot_col1:
            if st.button("↻ Rotate 90°", key="btn_rot_90"):
                st.session_state["rotation_angle"] = (st.session_state["rotation_angle"] - 90) % 360
                st.rerun()
        with rot_col2:
            if st.button("Flip 180°", key="btn_rot_180"):
                st.session_state["rotation_angle"] = (st.session_state["rotation_angle"] + 180) % 360
                st.rerun()

        # Get rotated image bytes for OCR cache key
        buf = BytesIO()
        pil_img.save(buf, format="JPEG", quality=95)
        active_bytes = buf.getvalue()
        cache_key = hashlib.md5(active_bytes).hexdigest()

        if st.session_state.get("active_ocr_key") != cache_key:
            with st.spinner("Analyzing card text with offline OCR..."):
                ocr_output = run_ocr_on_bytes(active_bytes)
                if ocr_output:
                    st.session_state["active_extracted"] = parse_card_elements(ocr_output)
                else:
                    st.session_state["active_extracted"] = None
            st.session_state["active_ocr_key"] = cache_key

        extracted_data = st.session_state.get("active_extracted")
        if extracted_data is None:
            st.warning("No readable text detected. Please ensure the card is clear and well-lit.")
    else:
        st.session_state["active_ocr_key"] = None
        st.session_state["active_extracted"] = None

with col_review:
    st.markdown('<div class="section-tag">▸ 02. VERIFY & SAVE RECORD</div>', unsafe_allow_html=True)

    if extracted_data:
        with st.form("verify_contact_form", clear_on_submit=False):
            r1_c1, r1_c2 = st.columns(2)
            with r1_c1:
                f_name = st.text_input("Full Name", value=extracted_data.get("Name", ""))
            with r1_c2:
                f_desig = st.text_input("Designation / Title", value=extracted_data.get("Designation", ""))

            r2_c1, r2_c2 = st.columns(2)
            with r2_c1:
                f_comp = st.text_input("Company / Organization", value=extracted_data.get("Company", ""))
            with r2_c2:
                f_phone = st.text_input("Phone Number(s)", value=extracted_data.get("Phone", ""))

            r3_c1, r3_c2 = st.columns(2)
            with r3_c1:
                f_email = st.text_input("Email Address", value=extracted_data.get("Email", ""))
            with r3_c2:
                f_web = st.text_input("Website", value=extracted_data.get("Website", ""))

            f_addr = st.text_area("Full Address", value=extracted_data.get("Address", ""), height=80)

            save_submit = st.form_submit_button("SAVE RECORD TO DATABASE", type="primary", use_container_width=True)
            if save_submit:
                df_curr = load_contacts()
                new_contact = pd.DataFrame([{
                    "Name": f_name.strip(),
                    "Designation": f_desig.strip(),
                    "Company": f_comp.strip(),
                    "Phone": f_phone.strip(),
                    "Email": f_email.strip(),
                    "Website": f_web.strip(),
                    "Address": f_addr.strip(),
                }])
                df_curr = pd.concat([df_curr, new_contact], ignore_index=True)
                save_contacts(df_curr)
                st.success(f"✓ Saved contact: {f_name or 'Card Record'}")
                st.rerun()
    else:
        st.markdown(
            """
            <div class="empty-placeholder">
                Upload or capture a visiting card on the left.<br>
                Fields will auto-populate here for instant verification and saving.
            </div>
            """,
            unsafe_allow_html=True,
        )

# --- Database & Export Section ---
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="section-tag">▸ 03. CONTACT DIRECTORY & EXPORT</div>', unsafe_allow_html=True)

latest_contacts = load_contacts()
if not latest_contacts.empty:
    search_query = st.text_input("🔍 Search Contacts (by Name, Company, or Email)", placeholder="Type to filter records...")
    
    display_df = latest_contacts
    if search_query.strip():
        q = search_query.strip().lower()
        display_df = latest_contacts[
            latest_contacts["Name"].str.lower().str.contains(q)
            | latest_contacts["Company"].str.lower().str.contains(q)
            | latest_contacts["Email"].str.lower().str.contains(q)
        ]

    edited_table = st.data_editor(
        display_df,
        num_rows="dynamic",
        use_container_width=True,
        key="contacts_table",
    )

    act1, act2, act3, act4 = st.columns([1.2, 1.2, 1.2, 2])
    with act1:
        if st.button("UPDATE EDITS", use_container_width=True):
            save_contacts(edited_table)
            st.success("Changes saved!")
            st.rerun()
    with act2:
        st.download_button(
            label="DOWNLOAD CSV",
            data=edited_table.to_csv(index=False).encode("utf-8"),
            file_name="contacts.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with act3:
        st.download_button(
            label="DOWNLOAD EXCEL (.XLSX)",
            data=to_excel_bytes(edited_table),
            file_name="contacts.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with act4:
        if st.button("RESET DATABASE", use_container_width=True):
            save_contacts(pd.DataFrame(columns=COLUMNS))
            st.warning("Database cleared.")
            st.rerun()
else:
    st.markdown(
        """
        <div class="empty-placeholder">
            No contacts saved yet. Scan a card above to start your directory.
        </div>
        """,
        unsafe_allow_html=True,
    )
