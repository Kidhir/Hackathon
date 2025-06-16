import streamlit as st
from PIL import Image
import os
import json
import uuid
import google.generativeai as genai

# ----------------------------
# CONFIGURATION
# ----------------------------

# Replace with your actual Gemini API Key
GEMINI_API_KEY = "AIzaSyAmZt-Pa31lf6TAZ_8p3S6qT2L8dNi-S1c"
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")

# ----------------------------
# UTILITY FUNCTIONS
# ----------------------------

def generate_accessible_alt(description: str) -> str:
    prompt = (
        f"Convert the following raw image description into accessible and concise alt text "
        f"according to WCAG 2.1 best practices:\n\nDescription: {description}\n\nAlt Text:"
    )
    response = model.generate_content(prompt)
    return response.text.strip()

def generate_mock_description(filename):
    base = os.path.splitext(filename)[0]
    return f"An image possibly depicting a scene related to '{base.replace('_', ' ')}'."

# ----------------------------
# STREAMLIT UI
# ----------------------------

st.set_page_config(page_title="Auto Alt Text Generator", layout="wide")
st.title("🧠 Auto Alt Text Generator for Images")

UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALT_TEXT_DB = "alt_text_data.json"
if os.path.exists(ALT_TEXT_DB):
    with open(ALT_TEXT_DB, "r") as f:
        alt_data = json.load(f)
else:
    alt_data = {}

uploaded_files = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    st.subheader("📸 Uploaded Images")
    for file in uploaded_files:
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.name}")
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())

        image = Image.open(file_path)
        st.image(image, width=250, caption=file.name)

        current_alt = alt_data.get(file.name, "")
        suggested_alt = st.text_input(f"✏️ Suggested Alt Text for {file.name}", value=current_alt or "")

        final_alt = st.text_input(f"✅ Final Alt Text for {file.name}", value=suggested_alt)
        if st.button(f"💾 Save Alt Text for {file.name}"):
            alt_data[file.name] = final_alt
            with open(ALT_TEXT_DB, "w") as f:
                json.dump(alt_data, f, indent=2)
            st.success("Alt Text Saved!")

    # Button: Auto Generate All Alt Texts
    if st.button("🤖 Auto-Generate Alt Texts with Gemini"):
        for file in uploaded_files:
            filename = file.name
            file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.name}")
            mock_desc = generate_mock_description(filename)

            with st.spinner(f"Generating alt text for {filename}..."):
                alt_text = generate_accessible_alt(mock_desc)
                alt_data[filename] = alt_text
                st.success(f"✅ Alt for {filename}: {alt_text}")

        with open(ALT_TEXT_DB, "w") as f:
            json.dump(alt_data, f, indent=2)

    st.markdown("---")
    if st.button("📄 Export Alt Text Report"):
        st.download_button(
            label="Download JSON",
            data=json.dumps(alt_data, indent=2),
            file_name="alt_text_report.json",
            mime="application/json"
        )
