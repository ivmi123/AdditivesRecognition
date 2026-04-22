import streamlit as st
import easyocr
from PIL import Image
import numpy as np

st.set_page_config(page_title="Additive Scanner OCR", layout="centered")

st.title("🧪 Food Additive Scanner (OCR)")
st.write("Upload a food label image to detect potentially harmful additives.")

# Initialize OCR reader (supports English + Bulgarian)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en', 'bg'])

reader = load_reader()

# Additives list
BAD_ADDITIVES = [
    "Titanium dioxide", "Титанов диоксид", "E171",
    "Potassium bromate", "Калиев бромат", "E924",
    "Sodium nitrite", "Натриев нитрит", "E250",
    "Potassium nitrite", "Калиев нитрит", "E249",
    "BHA Butylated hydroxy anisole", "BHA Бутилиран хидроксианизол", "E320",
    "BHT Butylated hydroxytoluene", "BHT Бутилиран хидрокситолуен", "E321",
    "TBHQ Tertiary butylhydroquinone", "TBHQ Третичен бутилхидрохинон", "E319",
    "Propyl paraben", "Пропилпарабен", "E216",
    "Butylparaben", "Бутилпарабен", "E209",
    "Brominated vegetable oil", "Бромирано растително масло", "E443",
    "Azodicarbonamide", "Азодикарбонамид", "E927a",
    "Aluminum compounds", "Алуминиеви съединения", "E173", "E520", "E521", "E522", "E523",
    "Carrageenan degraded form", "Карагенан разградена форма", "E407",
    "Polysorbate 80", "Полисорбат 80", "E433",
    "Carboxymethyl cellulose", "Карбоксиметилцелулоза", "E466"
]

# Normalize list
BAD_ADDITIVES = [a.lower() for a in BAD_ADDITIVES]

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    with st.spinner("🔍 Reading text..."):
        result = reader.readtext(np.array(image), detail=0)

    extracted_text = " ".join(result).lower()

    st.subheader("📄 Extracted Text")
    st.write(" ".join(result))

    found = []

    for additive in BAD_ADDITIVES:
        if additive in extracted_text:
            found.append(additive)

    st.subheader("⚠️ Detected Additives")

    if found:
        unique_found = sorted(set(found))
        for item in unique_found:
            st.error(f"Found: {item}")
    else:
        st.success("✅ No flagged additives detected!")
