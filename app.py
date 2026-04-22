import streamlit as st
import easyocr
from PIL import Image, ImageDraw
import numpy as np
import pandas as pd
from rapidfuzz import fuzz
import cv2
from pyzbar.pyzbar import decode

st.set_page_config(page_title="Advanced Additive Scanner", layout="centered")

st.title("🧪 Advanced Food Additive Scanner")

# Load OCR
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en', 'bg'])

reader = load_reader()

# Additives with classification
ADDITIVES = {
    "Titanium dioxide": "BANNED", "Титанов диоксид": "BANNED", "E171": "BANNED",
    "Potassium bromate": "BANNED", "Калиев бромат": "BANNED", "E924": "BANNED",
    "Sodium nitrite": "CAUTION", "Натриев нитрит": "CAUTION", "E250": "CAUTION",
    "Potassium nitrite": "CAUTION", "Калиев нитрит": "CAUTION", "E249": "CAUTION",
    "BHA": "CAUTION", "E320": "CAUTION",
    "BHT": "CAUTION", "E321": "CAUTION",
    "TBHQ": "CAUTION", "E319": "CAUTION",
    "Propyl paraben": "CAUTION", "E216": "CAUTION",
    "Butylparaben": "CAUTION", "E209": "CAUTION",
    "Brominated vegetable oil": "BANNED", "E443": "BANNED",
    "Azodicarbonamide": "BANNED", "E927a": "BANNED",
    "Aluminum compounds": "CAUTION",
    "E173": "CAUTION", "E520": "CAUTION", "E521": "CAUTION", "E522": "CAUTION", "E523": "CAUTION",
    "Carrageenan": "CAUTION", "E407": "CAUTION",
    "Polysorbate 80": "CAUTION", "E433": "CAUTION",
    "Carboxymethyl cellulose": "CAUTION", "E466": "CAUTION"
}

uploaded_file = st.file_uploader("Upload food label image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    img_np = np.array(image)

    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Barcode detection
    barcodes = decode(img_np)
    if barcodes:
        st.subheader("📦 Barcode detected")
        for b in barcodes:
            st.write(f"Code: {b.data.decode('utf-8')}")

    with st.spinner("🔍 Running OCR..."):
        results = reader.readtext(img_np)

    draw = ImageDraw.Draw(image)

    extracted_words = []
    detections = []

    for (bbox, text, prob) in results:
        extracted_words.append(text)

        # Draw bounding box
        pts = [tuple(map(int, p)) for p in bbox]
        draw.polygon(pts, outline="red")

        detections.append(text)

    st.image(image, caption="Detected Text with Boxes", use_column_width=True)

    full_text = " ".join(extracted_words).lower()

    st.subheader("📄 Extracted Text")
    st.write(" ".join(extracted_words))

    st.subheader("⚠️ Detected Additives")

    found = []

    for additive, risk in ADDITIVES.items():
        additive_lower = additive.lower()

        # Fuzzy match against full text
        score = fuzz.partial_ratio(additive_lower, full_text)

        if score > 80:
            found.append((additive, risk, score))

    if found:
        df = pd.DataFrame(found, columns=["Additive", "Risk", "Confidence"])
        df = df.drop_duplicates()

        st.dataframe(df)

        # Color-coded output
        for _, row in df.iterrows():
            if row["Risk"] == "BANNED":
                st.error(f"{row['Additive']} → 🚫 BANNED")
            elif row["Risk"] == "CAUTION":
                st.warning(f"{row['Additive']} → ⚠️ CAUTION")
            else:
                st.success(f"{row['Additive']} → ✅ SAFE")

        # Export CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Report (CSV)", csv, "report.csv", "text/csv")

    else:
        st.success("✅ No risky additives detected")
