import streamlit as st
import numpy as np
import pandas as pd
from rapidfuzz import fuzz
import easyocr
from PIL import Image, ImageDraw

st.set_page_config(page_title="Advanced Additive Scanner", layout="centered")

st.title("🧪 Advanced Food Additive Scanner")

st.markdown("""
This application scans food labels and detects harmful additives using OCR technology.
It also explains:
- what the additives are;
- possible health risks;
- healthier food alternatives.
""")

# =========================
# LOAD OCR READER
# =========================

@st.cache_resource
def load_reader():
    return easyocr.Reader(['en', 'bg'])

reader = load_reader()

# =========================
# ADDITIVES DATABASE
# =========================

ADDITIVES = {
    "E171": {
        "name": "Titanium Dioxide",
        "risk": "BANNED",
        "description": "Used as a white coloring agent in sweets and sauces.",
        "health": "May damage DNA and cause inflammation.",
        "alternative": "Foods with natural coloring."
    },

    "E250": {
        "name": "Sodium Nitrite",
        "risk": "CAUTION",
        "description": "Preservative used in processed meats.",
        "health": "May increase cancer risk and blood pressure.",
        "alternative": "Fresh meat without preservatives."
    },

    "E249": {
        "name": "Potassium Nitrite",
        "risk": "CAUTION",
        "description": "Used for preserving meat products.",
        "health": "Can form carcinogenic compounds.",
        "alternative": "Organic meat products."
    },

    "E320": {
        "name": "BHA",
        "risk": "CAUTION",
        "description": "Artificial antioxidant used to extend shelf life.",
        "health": "May cause hormonal and liver problems.",
        "alternative": "Foods without artificial preservatives."
    },

    "E321": {
        "name": "BHT",
        "risk": "CAUTION",
        "description": "Synthetic antioxidant added to snacks.",
        "health": "May affect hormones and the nervous system.",
        "alternative": "Natural snacks and homemade foods."
    },

    "E407": {
        "name": "Carrageenan",
        "risk": "CAUTION",
        "description": "Thickener used in dairy products.",
        "health": "May cause stomach irritation.",
        "alternative": "Natural yogurt and dairy."
    },

    "E433": {
        "name": "Polysorbate 80",
        "risk": "CAUTION",
        "description": "Emulsifier used in desserts and sauces.",
        "health": "May affect gut bacteria.",
        "alternative": "Homemade desserts."
    },

    "E466": {
        "name": "Carboxymethyl Cellulose",
        "risk": "CAUTION",
        "description": "Used to improve texture.",
        "health": "May cause digestive problems.",
        "alternative": "Fresh unprocessed foods."
    },

    "E924": {
        "name": "Potassium Bromate",
        "risk": "BANNED",
        "description": "Used in bread production.",
        "health": "Linked to cancer risk.",
        "alternative": "Bakery products without additives."
    }
}

# =========================
# FILE UPLOAD
# =========================

uploaded_file = st.file_uploader(
    "📤 Upload food label image",
    type=["jpg", "jpeg", "png"]
)

# =========================
# PROCESS IMAGE
# =========================

if uploaded_file:

    image = Image.open(uploaded_file)
    img_np = np.array(image)

    st.image(image, caption="Uploaded Image", use_column_width=True)

    with st.spinner("🔍 Running OCR..."):
        results = reader.readtext(img_np)

    draw = ImageDraw.Draw(image)

    extracted_words = []

    # Draw OCR boxes
    for (bbox, text, prob) in results:

        extracted_words.append(text)

        pts = [tuple(map(int, p)) for p in bbox]
        draw.polygon(pts, outline="red", width=2)

    st.image(
        image,
        caption="Detected Text with OCR Boxes",
        use_column_width=True
    )

    # =========================
    # EXTRACTED TEXT
    # =========================

    full_text = " ".join(extracted_words).lower()

    st.subheader("📄 Extracted Text")
    st.write(" ".join(extracted_words))

    # =========================
    # DETECT ADDITIVES
    # =========================

    st.subheader("⚠️ Detected Additives")

    found = []

    for additive_code, info in ADDITIVES.items():

        score = fuzz.partial_ratio(
            additive_code.lower(),
            full_text
        )

        if score > 80:

            found.append({
                "Code": additive_code,
                "Name": info["name"],
                "Risk": info["risk"],
                "Confidence": score
            })

    # =========================
    # SHOW RESULTS
    # =========================

    if found:

        df = pd.DataFrame(found).drop_duplicates()

        st.dataframe(df)

        danger_score = 0

        # Detailed information
        for item in found:

            code = item["Code"]
            info = ADDITIVES[code]

            st.markdown("---")

            st.subheader(f"🧪 {info['name']} ({code})")

            st.write(f"📌 Description: {info['description']}")

            st.write(f"🩺 Health Risks: {info['health']}")

            st.write(f"🥗 Healthy Alternative: {info['alternative']}")

            if info["risk"] == "BANNED":

                st.error("🚫 BANNED ADDITIVE")

                danger_score += 2

            elif info["risk"] == "CAUTION":

                st.warning("⚠️ USE WITH CAUTION")

                danger_score += 1

        # =========================
        # HEALTH SCORE
        # =========================

        st.markdown("---")

        st.subheader("📊 Product Health Score")

        if danger_score == 0:

            st.success("✅ SAFE PRODUCT")

            st.progress(100)

        elif danger_score <= 3:

            st.warning("⚠️ MODERATE RISK PRODUCT")

            st.progress(60)

        else:

            st.error("🚫 HIGH RISK PRODUCT")

            st.progress(30)

        # =========================
        # DOWNLOAD REPORT
        # =========================

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📥 Download CSV Report",
            csv,
            "food_report.csv",
            "text/csv"
        )

    else:

        st.success("✅ No risky additives detected.")

        st.progress(100)

    # =========================
    # HEALTHY ALTERNATIVES
    # =========================

    st.markdown("---")

    st.subheader("🥗 Healthy Food Alternatives")

    st.write("""
    ✅ Chips → Homemade baked potatoes  
    ✅ Soda → Natural juice or water  
    ✅ Processed meat → Fresh meat  
    ✅ Instant noodles → Homemade soup  
    ✅ Artificial desserts → Homemade desserts  
    ✅ Packaged snacks → Fruits and nuts  
    """)

    # =========================
    # FINAL MESSAGE
    # =========================

    st.markdown("---")

    st.info("""
    This project helps users make healthier food choices
    by identifying dangerous additives in packaged foods.
    """)
