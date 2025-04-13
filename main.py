import streamlit as st
import pandas as pd
from cryptography.fernet import Fernet
import json
import os

st.set_page_config(page_title="Scalable Anonymizer with Decryption")

# generate encryption key
key_file = "fernet.key"
if os.path.exists(key_file):
    with open(key_file, "rb") as f:
        key = f.read()
else:
    key = Fernet.generate_key()
    with open(key_file, "wb") as f:
        f.write(key)

fernet = Fernet(key)

# create mapping file
map_file = "anonymization_map.json"
if os.path.exists(map_file):
    with open(map_file, "r") as f:
        anon_map = json.load(f)
else:
    anon_map = {}

# Invert map for decryption
inverse_map = {v: k for k, v in anon_map.items()}

st.subheader("🔐 Scalable Column Anonymizer + Decryptor")
uploaded_file = st.file_uploader("📂 Upload your dataset (CSV)", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("### Preview of Uploaded Data", df.head())

    mode = st.radio("Choose Action:", ["Encrypt Column", "Decrypt Column"])

    if mode == "Encrypt Column":
        column = st.selectbox("Select column to anonymize", df.columns)

        if st.button("🔒 Encrypt"):
            unique_values = df[column].dropna().unique()
            for val in unique_values:
                if val not in anon_map:
                    encrypted = fernet.encrypt(val.encode()).decode()
                    anon_map[val] = encrypted

            # Save updated map
            with open(map_file, "w") as f:
                json.dump(anon_map, f, indent=2)

            df[column + "_Encrypted"] = df[column].map(anon_map)
            st.success("Encryption complete ✅")
            st.write(df.head())

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Encrypted File", csv, "encrypted_output.csv", "text/csv")

    elif mode == "Decrypt Column":
        encrypted_cols = [col for col in df.columns if col.endswith("_Encrypted")]
        if encrypted_cols:
            enc_col = st.selectbox("Select encrypted column", encrypted_cols)

            if st.button("🔓 Decrypt"):
                df[enc_col.replace("_Encrypted", "_Decrypted")] = df[enc_col].map(inverse_map)
                st.success("Decryption complete ✅")
                st.write(df.head())

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Download Decrypted File", csv, "decrypted_output.csv", "text/csv")
        else:
            st.warning("⚠️ No encrypted column found. Please upload a dataset with '_Encrypted' column.")
