import os
os.system("pip install xlsxwriter")
import streamlit as st
import pandas as pd
import re
from datetime import datetime
import io

st.set_page_config(page_title="Sensor Query Extractor", layout="wide")
st.title("📦 Sensor Query Cleaner + Auto Tagger")

uploaded_file = st.file_uploader("📄 Upload WhatsApp chat .txt file", type="txt")

# --- Auto-tag sensor types ---
sensor_keywords = {
    "Proximity": ["e2e", "e2b", "proximity", "tl-w", "tl-w5", "tlq", "tl-n", "pnp", "npn"],
    "Reed Switch": ["reed", "magnetic"],
    "Photoelectric": ["e3fa", "e3jk", "e3x", "e3c", "photo", "photocell"],
    "Capacitive": ["ec2", "ec5", "capacitive"],
    "Inductive": ["inductive"],
    "Pressure": ["pressure", "dz"],
    "Temperature": ["temperature", "pt100"],
    "Other": []
}

def auto_tag(product_name):
    product_name = product_name.lower()
    for tag, keywords in sensor_keywords.items():
        if any(k in product_name for k in keywords):
            return tag
    return "Other"

# --- Discard phrases ---
discard_phrases = [
    "send", "u sell", "u don't", "if get", "then buy", "may take", "i think", "this is",
    "have this", "available", "sensing price", "each", "immediate", "packing", "version",
    "duplicate", "original", "chinese", "best", "price", "import", "stamp", "plug", "cable",
    "extra dalwa", "check kar lena", "confirm", "image omitted", "sir", "done", "rate dena",
    "update", "just sent", "is this okay", "check this", "same", "ok", "ho sakta hai",
    "dekh lena", "will share", "photo", "image", "not dispatch", "this sensor", "sensor update",
    "dispatch", "ready", "send photo", "send image", "this one", "share", "kindly",
    "missed voice call", "call back", "courier details", "delivery", "model no", "yes", "no",
    "voice call", "sec", "omitted", "call", "audio omitted", "video omitted", "document omitted",
    "location omitted", "contact omitted", "sticker omitted", "gif omitted", "deleted",
    "this message was deleted", "calling", "busy", "ringing", "missed call", "declined"
]

# --- Extract helpers ---
def extract_date(line):
    match = re.search(r"\[(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})", line)
    if match:
        day, month, year = match.groups()
        if len(year) == 2:
            year = '20' + year
        return f"{year}-{int(month):02d}-{int(day):02d}"
    return None

def extract_quantity(text):
    if pd.isna(text): return None
    text = str(text).lower()
    match = re.search(r'(qty\s*\d+|\d+\s*pcs\b|\d+\s*nos\b|\d+\s*each\b|\d+\s*no\b)', text)
    return match.group(0) if match else None

def remove_quantity(text):
    return re.sub(r'(qty\s*\d+|\d+\s*pcs\b|\d+\s*nos\b|\d+\s*each\b|\d+\s*no\b)', '', str(text), flags=re.IGNORECASE).strip()

def remove_context(text):
    text = str(text)
    patterns = [
        r'\bwe\s*require\b', r'\bwe\s*need\b', r'\bneed\b', r'\brequirement\s*of\b',
        r'\bwe\s*are\s*looking\s*for\b', r'\blooking\s*for\b', r'\bsend\s*me\b',
        r'\bcan\s*you\s*send\b', r'\bcan\s*you\s*share\b', r'\bgive\s*me\b',
        r'\bi\s*want\b', r'\bi\s*need\b', r'\bpls\s*share\b', r'\bplease\s*share\b',
        r'\bkindly\s*share\b', r'\bshare\s*the\b', r'\bsend\s*the\b'
    ]
    for p in patterns:
        text = re.sub(p, '', text, flags=re.IGNORECASE)
    return text.strip()

def remove_sender(text):
    # Remove sender like "Majisha -5 :", "Box Silvassa :", etc.
    if ":" in text:
        return ":".join(text.split(":")[1:]).strip()
    return text.strip()

def clean_product(text):
    text = remove_sender(text)
    text = remove_quantity(text)
    text = remove_context(text)
    text = re.sub(r"[^\w\s\-_/.,]", "", text)  # remove special chars
    return text.strip()

def is_valid_product_query(text):
    """Check if the text represents a valid product query - must be actual product name/model"""
    if not text or len(text.strip()) < 2:
        return False
    
    text_lower = text.lower().strip()
    
    # Check for discard phrases
    if any(phrase in text_lower for phrase in discard_phrases):
        return False
    
    # Reject if it's just a conversational message
    conversational_starts = ["send", "u sell", "u don't", "if get", "then buy", "may take", "i think", "this is", "have this", "available", "in best", "for"]
    if any(text_lower.startswith(phrase) for phrase in conversational_starts):
        return False
    
    # Reject if it ends with conversational terms
    conversational_ends = ["each", "immediate", "packing", "version", "duplicate", "original", "chinese", "best", "price", "available", "please", "kya", "automation"]
    if any(text_lower.endswith(phrase) for phrase in conversational_ends):
        return False
    
    # Must have alphanumeric model pattern
    has_model_pattern = bool(re.search(r'[a-zA-Z]+\d+|[a-zA-Z]*\d+[a-zA-Z]+|\d+[a-zA-Z]+', text))
    
    # Must have technical specifications with units
    has_tech_specs = bool(re.search(r'\d+\s*(mm|cm|inch|bar|psi|v|volt|amp|mpa|kg|ton)', text_lower))
    
    # Must have sensor/product keywords
    product_keywords = ["sensor", "switch", "relay", "motor", "valve", "actuator", "controller", "encoder", "transmitter", "transducer"]
    has_product_keyword = any(keyword in text_lower for keyword in product_keywords)
    
    # Known brands with model numbers
    known_brands = ["omron", "festo", "sick", "banner", "schneider", "siemens", "allen", "bradley", "pepperl", "fuchs", "turck", "balluff"]
    has_brand_with_model = any(brand in text_lower for brand in known_brands) and has_model_pattern
    
    # Single brand names are not valid queries
    words = text_lower.split()
    if len(words) == 1 and words[0] in known_brands:
        return False
    
    # Must satisfy at least one condition
    return has_model_pattern or has_tech_specs or has_product_keyword or has_brand_with_model

# --- Main logic ---
if uploaded_file:
    raw_text = uploaded_file.read().decode("utf-8", errors="ignore")
    lines = raw_text.splitlines()
    records = []

    for line in lines:
        if not line.strip(): continue
        if not re.search(r"\[\d{1,2}/\d{1,2}/\d{2,4}", line): continue

        date = extract_date(line)
        msg_part = line.split("]")[-1] if "]" in line else line
        quantity = extract_quantity(msg_part)
        product_name = clean_product(msg_part)

        # Enhanced validation - only keep valid product queries
        if product_name and is_valid_product_query(product_name):
            sensor_type = auto_tag(product_name)
            records.append({
                "Product Line": line.strip(),
                "Product Name (with Model)": product_name,
                "Sensor Type": sensor_type,
                "Extracted Quantity": quantity,
                "Date": date
            })

    if records:
        df = pd.DataFrame(records)
        st.success(f"✅ Extracted {len(records)} Valid Product Queries")
        st.dataframe(df)

        # --- Download Excel ---
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Sensor Queries")
        st.download_button(
            label="⬇ Download Excel",
            data=output.getvalue(),
            file_name="sensor_queries_cleaned_tagged.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Show statistics
        st.subheader("📊 Query Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Queries", len(records))
        with col2:
            st.metric("Sensor Types", df['Sensor Type'].nunique())
        with col3:
            queries_with_qty = df[df['Extracted Quantity'].notna()]['Extracted Quantity'].count()
            st.metric("With Quantity", queries_with_qty)
        
        # Show sensor type distribution
        st.subheader("🔧 Sensor Type Distribution")
        sensor_counts = df['Sensor Type'].value_counts()
        st.bar_chart(sensor_counts)
        
    else:
        st.warning("⚠ No valid product queries found in the uploaded file.")
