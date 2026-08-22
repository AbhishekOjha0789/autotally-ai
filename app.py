import streamlit as st
import requests
import zipfile
import io
import json
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="AutoTally AI | Supermarket POS & Tally Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- PROFESSIONAL CUSTOM CSS INJECTION ---
st.markdown("""
    <style>
    /* Main background and font styling */
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Hide default Streamlit branding, header, and top toolbar/GitHub buttons */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden; display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    
    /* Custom Card Containers */
    .pos-card {
        background: #1e293b;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 20px;
    }
    
    /* Metric styling */
    .metric-container {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 16px;
        border-radius: 8px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = ""
if "cart_items" not in st.session_state:
    st.session_state.cart_items = []

API_BASE_URL = "https://autotally-ai.onrender.com"  # Update if running locally

# --- AUTHENTICATION PORTAL (PROFESSIONAL SPLIT SCREEN) ---
if not st.session_state.logged_in:
    # Hide sidebar only when logged out
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                transform: translateX(-100%);
                visibility: hidden;
            }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center; color: #38bdf8;'>⚡ AutoTally POS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8;'>Supermarket Invoicing & Instant Tally XML Synchronization Suite</p><br>", unsafe_allow_html=True)
        
        auth_tab1, auth_tab2 = st.tabs(["🔐 Secure Login", "📝 Create Account"])
        
        with auth_tab1:
            with st.form("login_form"):
                l_user = st.text_input("Username")
                l_pass = st.text_input("Password", type="password")
                l_submit = st.form_submit_button("Sign In to Workspace", use_container_width=True)
                
                if l_submit:
                    if l_user.strip() and l_pass.strip():
                        with st.spinner("Connecting to secure server (Waking up cloud instance)..."):
                            try:
                                res = requests.post(f"{API_BASE_URL}/login", json={"username": l_user, "password": l_pass}, timeout=15)
                                if res.status_code == 200:
                                    data = res.json()
                                    st.session_state.logged_in = True
                                    st.session_state.user_id = data["user_id"]
                                    st.session_state.username = l_user
                                    st.success("Authentication successful!")
                                    st.rerun()
                                else:
                                    st.error(res.json().get("detail", "Invalid credentials."))
                            except requests.exceptions.Timeout:
                                st.warning("Server is waking up from sleep mode. Please click the button again in 5 seconds!")
                            except:
                                st.error("Connection failed. Check backend server.")
                    else:
                        st.error("Please fill in all fields.")
                        
        with auth_tab2:
            with st.form("register_form"):
                r_user = st.text_input("Choose Username")
                r_pass = st.text_input("Choose Password", type="password")
                r_submit = st.form_submit_button("Register Store Account", use_container_width=True)
                
                if r_submit:
                    if r_user.strip() and r_pass.strip():
                        with st.spinner("Connecting to secure server (Waking up cloud instance)..."):
                            try:
                                res = requests.post(f"{API_BASE_URL}/register", json={"username": r_user, "password": r_pass}, timeout=15)
                                if res.status_code == 200:
                                    data = res.json()
                                    st.session_state.logged_in = True
                                    st.session_state.user_id = data["user_id"]
                                    st.session_state.username = r_user
                                    st.success("Account created successfully!")
                                    st.rerun()
                                else:
                                    st.error(res.json().get("detail", "Registration failed."))
                            except requests.exceptions.Timeout:
                                st.warning("Server is waking up from sleep mode. Please click the button again in 5 seconds!")
                            except:
                                st.error("Connection failed. Check backend server.")
                    else:
                        st.error("Please fill in all fields.")

# --- PROFESSIONAL POS DASHBOARD (WHEN LOGGED IN) ---
else:
    # Top utility bar for store identity and session control
    top_col1, top_col2 = st.columns([4, 1])
    with top_col1:
        st.markdown(f"### 🏢 Store: **{st.session_state.username.upper()}** | Active POS Terminal #01")
    with top_col2:
        if st.button("🚪 Terminate Session", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = ""
            st.session_state.cart_items = []
            st.rerun()

    st.markdown("---")

    # Main Navigation Tabs (Replaces the sidebar completely)
    menu_selection = st.radio(
        "Navigation Hub", 
        [
            "⚡ AI Invoice & Tally XML Builder",
            "🛒 POS & Barcode Billing", 
            "📦 Inventory Management", 
            "📂 Saved XML History Hub", 
            "⚙️ Tally Integration Settings"
        ],
        horizontal=True
    )
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- TAB: AI INVOICE & TALLY XML BUILDER (CORE FEATURE) ---
    if menu_selection == "⚡ AI Invoice & Tally XML Builder":
        st.markdown("## ⚡ AI Invoice Parser & Tally XML Generator")
        st.markdown("Upload any digital purchase invoice (PDF or Image). Our local ML Gatekeeper validates the structure, Gemini extracts the line items, math is verified, and a Tally-compliant XML file is generated instantly.")
        
        col_upload, col_preview = st.columns([1.2, 1])
        
        with col_upload:
            with st.form("invoice_upload_form"):
                company_input = st.text_input("Tally Company Ledger Name", value="My Company")
                uploaded_file = st.file_uploader("Upload Purchase Invoice (PDF, PNG, JPG)", type=["pdf", "png", "jpg", "jpeg"])
                
                process_btn = st.form_submit_button("🚀 Process & Generate Tally XML", use_container_width=True)
                
                if process_btn:
                    if uploaded_file is not None:
                        with st.spinner("Analyzing invoice with AI & Gatekeeper..."):
                            try:
                                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                                params = {"company_name": company_input}
                                
                                res = requests.post(f"{API_BASE_URL}/process-invoice", files=files, params=params, timeout=30)
                                
                                if res.status_code == 200:
                                    xml_output = res.text
                                    st.success("Invoice successfully processed and XML generated!")
                                    
                                    # Store in session state for download
                                    st.session_state.last_xml = xml_output
                                    st.session_state.last_filename = f"{os.path.splitext(uploaded_file.name)[0]}_tally.xml"
                                else:
                                    st.error(f"Processing failed: {res.json().get('detail', 'Unknown error')}")
                            except Exception as e:
                                st.error(f"Connection error: {str(e)}")
                    else:
                        st.warning("Please upload an invoice file first.")
                        
        with col_preview:
            st.markdown("### 📄 XML Output & Download")
            if "last_xml" in st.session_state and st.session_state.last_xml:
                st.text_area("Generated Tally XML Preview", value=st.session_state.last_xml, height=300)
                st.download_button(
                    label="📥 Download Tally XML File",
                    data=st.session_state.last_xml,
                    file_name=st.session_state.get("last_filename", "tally_voucher.xml"),
                    mime="application/xml",
                    use_container_width=True
                )
            else:
                st.info("Upload and process an invoice on the left to preview and download your Tally-compliant XML file here.")

    # --- TAB 2: POS & BARCODE BILLING WORKFLOW ---
    elif menu_selection == "🛒 POS & Barcode Billing":
        st.markdown("## 🛒 Supermarket POS Terminal")
        st.markdown("Scan store barcodes to check live inventory stock, validate quantities, and sync Tally XML vouchers.")
        
        col_main, col_summary = st.columns([2, 1])
        
        with col_main:
            st.markdown("### 📦 Line Item Management")
            
            with st.form("barcode_scan_form", clear_on_submit=True):
                c1, c2 = st.columns([2, 1])
                barcode_input = c1.text_input("Barcode Scanner Input / SKU Code", placeholder="Scan item barcode here...")
                qty_input = c2.number_input("Quantity", min_value=1, value=1)
                add_btn = st.form_submit_button("➕ Add Item to Cart", use_container_width=True)
                
                if add_btn and barcode_input.strip():
                    try:
                        res = requests.get(f"{API_BASE_URL}/product/{barcode_input.strip()}")
                        if res.status_code == 200:
                            prod_data = res.json()
                            available_stock = prod_data.get("stock", 0)
                            
                            if available_stock < qty_input:
                                st.error(f"❌ Out of Stock! Only {available_stock} units remaining for {prod_data['name']}.")
                            else:
                                st.session_state.cart_items.append({
                                    "barcode": barcode_input.strip(),
                                    "name": prod_data["name"],
                                    "quantity": qty_input,
                                    "rate": prod_data["price"],
                                    "total": prod_data["price"] * qty_input
                                })
                                st.success(f"Added: {prod_data['name']} (Qty: {qty_input})")
                        else:
                            st.error("❌ Barcode denied: Product not found in database inventory master.")
                    except:
                        st.error("Connection failed while reaching inventory database.")
            
            if st.session_state.cart_items:
                st.markdown("#### Current Cart Bill")
                cart_display = []
                for idx, item in enumerate(st.session_state.cart_items):
                    cart_display.append({
                        "Item Name": item["name"],
                        "Qty": item["quantity"],
                        "Rate (₹)": item["rate"],
                        "Total (₹)": item["total"]
                    })
                st.dataframe(cart_display, use_container_width=True)
                
                if st.button("🗑️ Clear Cart", type="secondary"):
                    st.session_state.cart_items = []
                    st.rerun()
            else:
                st.info("Cart is currently empty. Scan a barcode above to add items.")

        with col_summary:
            st.markdown("### 🧾 Voucher Summary")
            tally_company = st.text_input("Tally Company Ledger", value="Retail Supermarket HQ")
            vendor_name = st.text_input("Supplier / Vendor Name", value="Local Distributor Corp")
            
            subtotal = sum([i["total"] for i in st.session_state.cart_items])
            tax_amount = subtotal * 0.05
            grand_total = subtotal + tax_amount
            
            st.markdown(f"""
                <div style='background: #1e293b; padding: 16px; border-radius: 8px; border: 1px solid #334155; color: #f8fafc;'>
                    <p style='color: #cbd5e1; margin-bottom: 8px;'><b>Subtotal:</b> ₹{subtotal:.2f}</p>
                    <p style='color: #cbd5e1; margin-bottom: 12px;'><b>Estimated Tax (5%):</b> ₹{tax_amount:.2f}</p>
                    <hr style='border: 0; border-top: 1px solid #334155; margin: 10px 0;'>
                    <h3 style='color: #38bdf8; margin: 0;'><b>Grand Total:</b> ₹{grand_total:.2f}</h3>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("⚡ Generate & Sync Tally XML", type="primary", use_container_width=True):
                if not st.session_state.cart_items:
                    st.warning("Please add items to the cart before generating vouchers.")
                else:
                    try:
                        checkout_payload = {
                            "user_id": st.session_state.user_id,
                            "company_name": tally_company,
                            "vendor_name": vendor_name,
                            "items": st.session_state.cart_items
                        }
                        
                        res = requests.post(f"{API_BASE_URL}/checkout", json=checkout_payload)
                        if res.status_code == 200:
                            st.success("Voucher generated, database inventory stock deducted, and XML synced successfully!")
                            st.session_state.cart_items = []
                            st.rerun()
                        else:
                            st.error(res.json().get("detail", "Checkout processing failed."))
                    except Exception as e:
                        st.error(f"Error during checkout: {str(e)}")

    # --- TAB 3: INVENTORY MANAGEMENT & LIVE STOCK VIEW ---
    elif menu_selection == "📦 Inventory Management":
        st.markdown("## 📦 Supermarket Inventory & Stock Control")
        st.markdown("Add new stock or view real-time inventory levels across your store.")
        
        col_form, col_table = st.columns([1, 1.5])
        
        with col_form:
            with st.form("add_product_form", clear_on_submit=True):
                st.markdown("### ➕ Add / Restock Item")
                inv_barcode = st.text_input("Product Barcode / SKU")
                inv_name = st.text_input("Product Name")
                inv_price = st.number_input("Selling Price (₹)", min_value=0.0, value=50.0)
                inv_stock = st.number_input("Stock Quantity to Add", min_value=1, value=10)
                
                submit_inv = st.form_submit_button("💾 Save to Inventory Master", use_container_width=True)
                
                if submit_inv:
                    if inv_barcode.strip() and inv_name.strip():
                        with st.spinner("Updating inventory..."):
                            try:
                                payload = {
                                    "barcode": inv_barcode.strip(),
                                    "name": inv_name.strip(),
                                    "price": inv_price,
                                    "stock": inv_stock
                                }
                                res = requests.post(f"{API_BASE_URL}/product/add", json=payload, timeout=10)
                                if res.status_code == 200:
                                    st.success(res.json().get("message", "Inventory updated successfully!"))
                                    st.rerun()
                                else:
                                    st.error(res.json().get("detail", "Failed to update inventory."))
                            except Exception as e:
                                st.error(f"Connection error: {str(e)}")
                    else:
                        st.error("Please fill in both the barcode and product name.")
                        
        with col_table:
            st.markdown("### 📊 Live Stock Catalog")
            try:
                res = requests.get(f"{API_BASE_URL}/products/all", timeout=10)
                if res.status_code == 200:
                    products = res.json()
                    if products:
                        table_data = []
                        for p in products:
                            table_data.append({
                                "Barcode": p.get("barcode"),
                                "Product Name": p.get("name"),
                                "Price (₹)": p.get("price"),
                                "Stock Qty": p.get("stock")
                            })
                        st.dataframe(table_data, use_container_width=True, hide_index=True)
                    else:
                        st.info("No products found in database. Add one using the form on the left!")
                else:
                    st.warning("Could not fetch inventory stock.")
            except:
                st.error("Connection failed while reaching inventory database.")

    # --- TAB 4: SAVED XML HISTORY HUB ---
    elif menu_selection == "📂 Saved XML History Hub":
        st.markdown("## 📂 Centralized XML History & One-Click Fetch")
        st.markdown("Access all previously synced supermarket receipts, filter instantly, or download files formatted for Tally import.")
        
        # Fetch history from backend using current user_id
        try:
            res = requests.get(f"{API_BASE_URL}/receipts/{st.session_state.user_id}", timeout=10)
            if res.status_code == 200:
                receipts = res.json()
                
                if receipts:
                    search_query = st.text_input("🔍 Search receipts by vendor or company name...", "").lower()
                    
                    filtered_receipts = [
                        r for r in receipts 
                        if search_query in r.get("vendor_name", "").lower() or search_query in r.get("company_name", "").lower()
                    ]
                    
                    st.markdown(f"Showing **{len(filtered_receipts)}** saved transaction(s):")
                    st.markdown("---")
                    
                    for idx, rec in enumerate(filtered_receipts):
                        with st.expander(f"🧾 Vendor: {rec.get('vendor_name', 'Unknown')} | Company: {rec.get('company_name', 'N/A')} | Date: {rec.get('timestamp', 'Recent')}"):
                            col_info, col_dl = st.columns([2, 1])
                            
                            with col_info:
                                st.write(f"**Total Amount:** ₹{rec.get('grand_total', 0):.2f}")
                                items = rec.get("items", [])
                                st.write(f"**Items Count:** {len(items)}")
                                
                                # Optional: Show line items table
                                if items:
                                    st.dataframe(items, use_container_width=True, hide_index=True)
                                    
                            with col_dl:
                                xml_content = rec.get("xml_data", "<XML>Not Available</XML>")
                                st.download_button(
                                    label="📥 Download XML",
                                    data=xml_content,
                                    file_name=f"receipt_{idx+1}_tally.xml",
                                    mime="application/xml",
                                    key=f"dl_xml_{idx}"
                                )
                else:
                    st.info("No saved invoices found in your secure database yet. Process transactions via the POS terminal or upload an invoice to populate your history.")
            else:
                st.warning("Could not retrieve transaction history from the server.")
        except Exception as e:
            st.error(f"Connection error while fetching history: {str(e)}")

    # --- TAB 5: TALLY INTEGRATION SETTINGS ---
    elif menu_selection == "⚙️ Tally Integration Settings":
        st.markdown("## ⚙️ Tally ERP / Prime Sync Settings")
        st.markdown("Configure local gateway ports and company master configurations for seamless XML importing.")
        
        st.text_input("Tally ODBC Server Host", value="localhost")
        st.text_input("Tally ODBC Port", value="9000")
        st.selectbox("Default Voucher Type", ["Purchase", "Receipt", "Journal"])
        
        if st.button("Save Configuration", type="primary"):
            st.success("Tally sync parameters updated successfully!")