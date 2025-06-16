# auto_alt_streamlit.py

import streamlit as st
from PIL import Image
import os
import json
import uuid

st.set_page_config(page_title="Auto Alt Text Generator", layout="wide")
st.title("🧠 Auto Alt Text Generator for Images")

# Directory to store uploaded images
UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize alt text data
ALT_TEXT_DB = "alt_text_data.json"
if os.path.exists(ALT_TEXT_DB):
    with open(ALT_TEXT_DB, "r") as f:
        alt_data = json.load(f)
else:
    alt_data = {}

# Upload images
uploaded_files = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
if uploaded_files:
    st.subheader("📸 Uploaded Images")
    for file in uploaded_files:
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.name}")
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())

        # Load and display image
        image = Image.open(file_path)
        st.image(image, width=200, caption=file.name)

        # Check existing alt (simulated)
        current_alt = alt_data.get(file.name, "")
        st.write(f"Current Alt Text: `{current_alt}`")

        # Placeholder for alt text generation (to be replaced by agent)
        suggested_alt = st.text_input(f"Suggested Alt Text for {file.name}", value=f"[AI Suggestion for {file.name}]")

        # Save final alt
        final_alt = st.text_input(f"Final Alt Text for {file.name}", value=current_alt or suggested_alt)
        if st.button(f"💾 Save Alt Text for {file.name}"):
            alt_data[file.name] = final_alt
            with open(ALT_TEXT_DB, "w") as f:
                json.dump(alt_data, f, indent=2)
            st.success("Saved!")

st.markdown("---")
if st.button("📄 Export Alt Text Report"):
    st.download_button(
        label="Download JSON",
        data=json.dumps(alt_data, indent=2),
        file_name="alt_text_report.json",
        mime="application/json"
    )
