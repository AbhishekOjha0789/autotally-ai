import streamlit as st
import requests
import zipfile
import io
from datetime import datetime

st.set_page_config(page_title="AutoTally AI", page_icon="🧾", layout="centered")

# Initialize session state for real backend user tracking
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = ""
if "history" not in st.session_state:
    st.session_state.history = []

# Replace with your actual backend URL (local or Render)
API_BASE_URL = "https://autotally-ai.onrender.com" 

# --- AUTHENTICATION SCREEN ---
if not st.session_state.logged_in:
    st.title("🧾 AutoTally AI - Portal")
    st.markdown("Please sign in or create an account to access your persistent database workspace.")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            login_user = st.text_input("Username")
            login_pass = st.text_input("Password", type="password")
            login_submit = st.form_submit_button("Login")
            
            if login_submit:
                if login_user.strip() and login_pass.strip():
                    try:
                        response = requests.post(f"{API_BASE_URL}/login", json={"username": login_user, "password": login_pass})
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.logged_in = True
                            st.session_state.user_id = data["user_id"]
                            st.session_state.username = login_user
                            st.success(f"Welcome back, {login_user}!")
                            st.rerun()
                        else:
                            st.error(response.json().get("detail", "Login failed."))
                    except requests.exceptions.ConnectionError:
                        st.error("Could not connect to the backend server.")
                else:
                    st.error("Please fill in all fields.")
                    
    with tab2:
        with st.form("register_form"):
            reg_user = st.text_input("Choose Username")
            reg_pass = st.text_input("Choose Password", type="password")
            reg_submit = st.form_submit_button("Create Account")
            
            if reg_submit:
                if reg_user.strip() and reg_pass.strip():
                    try:
                        response = requests.post(f"{API_BASE_URL}/register", json={"username": reg_user, "password": reg_pass})
                        if response.status_code == 200:
                            data = response.json()
                            st.session_state.logged_in = True
                            st.session_state.user_id = data["user_id"]
                            st.session_state.username = reg_user
                            st.success("Account created successfully! You are now logged in.")
                            st.rerun()
                        else:
                            st.error(response.json().get("detail", "Registration failed."))
                    except requests.exceptions.ConnectionError:
                        st.error("Could not connect to the backend server.")
                else:
                    st.error("Please fill in all fields.")

# --- MAIN DASHBOARD (WHEN LOGGED IN) ---
else:
    with st.sidebar:
        st.write(f"👤 Logged in as: **{st.session_state.username}**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = ""
            st.session_state.history = []
            st.rerun()
        st.markdown("---")
        st.markdown("### 📊 Platform Stats")
        st.metric("Total Receipts Processed", len(st.session_state.history))

    st.title("🧾 AutoTally AI Dashboard")
    st.markdown("Convert purchase invoices into Tally-compliant XML vouchers instantly using Gemini AI.")

    uploaded_file = st.file_uploader("Upload Purchase Invoice (PDF or Image)", type=["pdf", "png", "jpg", "jpeg"])
    company_name = st.text_input("Tally Company Name", value="My Company")

    st.info("Note: The backend runs on a free cloud tier and may take 30 seconds to wake up on the first request!")

    if uploaded_file is not None:
        if uploaded_file.type.startswith("image/"):
            st.image(uploaded_file, caption="Uploaded Invoice Preview", use_container_width=True)
        else:
            st.info(f"📄 PDF Uploaded: {uploaded_file.name}")
        
        if st.button("Process Invoice & Generate XML", type="primary"):
            with st.spinner("Analyzing invoice via Gemini AI and validating math..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    data = {"company_name": company_name, "user_id": st.session_state.user_id}
                    
                    response = requests.post(f"{API_BASE_URL}/process-invoice", files=files, data=data)
                    
                    if response.status_code == 200:
                        xml_output = response.text
                        st.success("Invoice successfully processed and verified!")
                        
                        # Save to local session log view
                        record = {
                            "filename": uploaded_file.name,
                            "vendor": "Parsed Vendor",
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "xml": xml_output
                        }
                        st.session_state.history.append(record)
                        
                        st.code(xml_output, language="xml")
                        
                        st.download_button(
                            label="Download Tally XML File",
                            data=xml_output,
                            file_name=f"{uploaded_file.name.rsplit('.', 1)[0]}_tally.xml",
                            mime="application/xml"
                        )
                    else:
                        error_detail = response.json().get("detail", "Unknown error")
                        st.error(f"Processing failed: {error_detail}")
                        
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the FastAPI backend.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")

    # --- HISTORY & FILTERABLE DOWNLOAD HUB ---
    if st.session_state.history:
        st.markdown("---")
        st.subheader("📂 Generated XML History & Batch Downloads")
        
        filter_query = st.text_input("Filter history by filename or keyword:", "").lower()
        
        filtered_history = [
            item for item in st.session_state.history 
            if filter_query in item["filename"].lower() or filter_query in item["vendor"].lower()
        ]
        
        for idx, item in enumerate(filtered_history):
            col1, col2, col3 = st.columns([3, 2, 2])
            col1.write(f"📄 **{item['filename']}**")
            col2.write(f"🕒 {item['date']}")
            with col3:
                st.download_button(
                    label="Download XML",
                    data=item["xml"],
                    file_name=f"{item['filename'].rsplit('.', 1)[0]}_tally.xml",
                    mime="application/xml",
                    key=f"dl_{idx}"
                )
        
        st.markdown("### 📦 Bulk Actions")
        if filtered_history:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for item in filtered_history:
                    safe_name = item["filename"].rsplit('.', 1)[0] + ".xml"
                    zip_file.writestr(safe_name, item["xml"])
            zip_buffer.seek(0)
            
            st.download_button(
                label="📥 Download Filtered Batch as ZIP",
                data=zip_buffer,
                file_name="autotally_filtered_batch.zip",
                mime="application/x-zip-compressed"
            )