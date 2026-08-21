import streamlit as st
import requests

st.set_page_config(page_title="AutoTally AI", page_icon="🧾", layout="centered")

st.title("🧾 AutoTally AI")
st.markdown("Automate the conversion of purchase invoices into Tally-compliant XML vouchers instantly using Gemini AI.")

# File uploader widget supporting PDFs and images
uploaded_file = st.file_uploader("Upload Purchase Invoice (PDF or Image)", type=["pdf", "png", "jpg", "jpeg"])

company_name = st.text_input("Tally Company Name", value="My Company")

st.info("Note: The backend runs on a free cloud tier and may take 30 seconds to wake up on the first request!")

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Invoice Preview", use_container_width=True)
    
    if st.button("Process Invoice & Generate XML", type="primary"):
        with st.spinner("Analyzing invoice via Gemini AI and validating math..."):
            try:
                # Prepare file payload for FastAPI backend
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {"company_name": company_name}
                
                # Call our local FastAPI backend
                response = requests.post("http://127.0.0.1:8000/process-invoice", files=files, data=data)
                
                if response.status_code == 200:
                    xml_output = response.text
                    st.success("Invoice successfully processed and verified!")
                    
                    # Display XML code block
                    st.code(xml_output, language="xml")
                    
                    # Download button for the generated XML file
                    st.download_button(
                        label="Download Tally XML File",
                        data=xml_output,
                        file_name="tally_voucher.xml",
                        mime="application/xml"
                    )
                else:
                    error_detail = response.json().get("detail", "Unknown error")
                    st.error(f"Processing failed: {error_detail}")
                    
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the FastAPI backend. Make sure your uvicorn server is running!")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")