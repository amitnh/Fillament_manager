import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Bambu Filament Manager", page_icon="🖨️", layout="wide")

# --- CSS Hacks to remove fade/transitions ---
st.markdown("""
<style>
    /* 1. Global transition reset */
    * {
        transition: none !important;
        animation: none !important;
    }
    
    /* 2. Force opacity to 1 to prevent graying out */
    .stApp {
        opacity: 1 !important;
    }
    
    /* 3. Hide the 'running' man icon if desired */
    .stStatusWidget {
        visibility: hidden;
    }
    
    /* 4. Specific Streamlit classes for the main container */
    section[data-testid="stSidebar"] {
        transition: none !important;
    }
    div[data-testid="stDecoration"] {
        display: none;
    }
    
    /* Custom Button Styling for Grid */
    div.stButton > button {
        width: 100%;
        height: 100%;
        white-space: normal;
        padding: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)
# ---------------------------------------------

st.title("🖨️ Bambu Lab Filament Manager")

# Sidebar Navigation
page = st.sidebar.radio("Navigate", ["Inventory", "Log Print", "Add Filament", "Stats"])

# Session state for manual selection modal logic if needed (simplified here)
if 'manual_cart' not in st.session_state:
    st.session_state.manual_cart = []

@st.cache_data(ttl=15, show_spinner=False)
def get_filaments():
    try:
        response = requests.get(f"{API_URL}/filaments")
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to Backend API. Is it running?")
        return []
    return []

if page == "Inventory":
    st.header("🧵 Filament Inventory")
    
    filaments = get_filaments()
    
    if not filaments:
        st.info("No filaments found. Add some in the 'Add Filament' tab!")
    else:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            show_low_stock = st.checkbox("Show Low Stock Only")
        
        if show_low_stock:
            filaments = [f for f in filaments if f['remaining_weight'] < 100]

        for f in filaments:
            with st.container():
                # Visual Color Box Logic
                color_hex = f.get('color_hex', '#000000')
                if not color_hex: color_hex = "#000000"
                
                if "," in color_hex:
                    colors = color_hex.split(",")
                    bg_style = f"background: linear-gradient(45deg, {colors[0]} 50%, {colors[1]} 50%);"
                else:
                    bg_style = f"background-color: {color_hex};"

                # Layout
                c1, c2, c3, c4 = st.columns([3, 3, 4, 2])
                
                with c1:
                    st.subheader(f"{f['brand']} {f['material']}")
                    st.caption(f"Color: {f['color_name']}")
                    st.caption(f"ID: {f['id']}")
                
                with c2:
                    # Color Preview
                    st.markdown(
                        f'<div style="{bg_style} width: 100%; height: 40px; border-radius: 5px; border: 1px solid #ccc; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);"></div>',
                        unsafe_allow_html=True
                    )
                    if f.get('is_multicolor'):
                        st.caption("🌈 Multi-color")
                
                with c3:
                    # Progress Bar & Weight
                    remaining = f['remaining_weight']
                    initial = f['initial_weight']
                    progress = max(0.0, min(1.0, remaining / initial))
                    
                    st.progress(progress)
                    st.write(f"**{remaining:.1f}g** / {initial:.0f}g")
                
                with c4:
                    # Edit Button
                    with st.expander("✏️ Edit"):
                        with st.form(f"edit_form_{f['id']}"):
                            # Editable fields
                            new_brand = st.text_input("Brand", value=f['brand'], key=f"brand_{f['id']}")
                            new_material = st.text_input("Material", value=f['material'], key=f"mat_{f['id']}")
                            new_color_name = st.text_input("Color Name", value=f['color_name'], key=f"cn_{f['id']}")
                            
                            new_weight = st.number_input("Current Weight (g)", value=float(remaining), key=f"w_{f['id']}")
                            new_price = st.number_input("Price ($)", value=float(f['price']), key=f"p_{f['id']}")
                            
                            # Color Editing
                            st.divider()
                            new_is_multicolor = st.checkbox("Multi-color?", value=f.get('is_multicolor', False), key=f"mc_{f['id']}")
                            
                            current_hex = f.get('color_hex', '#000000')
                            if not current_hex: current_hex = "#000000"
                            
                            new_color_hex = current_hex

                            if new_is_multicolor:
                                c_col1, c_col2 = st.columns(2)
                                # Try to parse existing colors
                                colors = ["#FF0000", "#0000FF"]
                                if "," in current_hex:
                                    parts = current_hex.split(",")
                                    if len(parts) >= 2:
                                        colors = [p.strip() for p in parts[:2]]
                                
                                with c_col1:
                                    col1 = st.color_picker("Color 1", value=colors[0] if colors[0].startswith("#") else "#FF0000", key=f"c1_{f['id']}")
                                with c_col2:
                                    col2 = st.color_picker("Color 2", value=colors[1] if colors[1].startswith("#") else "#0000FF", key=f"c2_{f['id']}")
                                new_color_hex = f"{col1},{col2}"
                            else:
                                # Single color
                                val = current_hex if "," not in current_hex and current_hex.startswith("#") else "#000000"
                                new_color_hex = st.color_picker("Color Hex", value=val, key=f"chex_{f['id']}")
                            
                            st.divider()

                            if st.form_submit_button("Update"):
                                payload = {
                                    "brand": new_brand,
                                    "material": new_material,
                                    "color_name": new_color_name,
                                    "remaining_weight": new_weight,
                                    "price": new_price,
                                    "color_hex": new_color_hex,
                                    "is_multicolor": new_is_multicolor
                                }
                                try:
                                    res = requests.put(f"{API_URL}/filament/{f['id']}", json=payload)
                                    if res.status_code == 200:
                                        st.success("Updated!")
                                        st.cache_data.clear()
                                        st.rerun()
                                    else:
                                        st.error(f"Error: {res.text}")
                                except Exception as e:
                                    st.error(f"Conn Error: {e}")

                st.divider()

elif page == "Add Filament":
    st.header("➕ Add New Spool")
    
    with st.form("new_filament_form"):
        col1, col2 = st.columns(2)
        with col1:
            brand = st.text_input("Brand", value="Bambu Lab")
            material = st.selectbox("Material", ["PLA", "PETG", "ABS", "ASA", "TPU", "PA-CF"])
            color_name = st.text_input("Color Name (e.g. Matte White)", value="Black")
            
            is_multicolor = st.checkbox("Dual Color / Gradient?")
            
        with col2:
            if is_multicolor:
                c_a, c_b = st.columns(2)
                with c_a:
                    color_1 = st.color_picker("Color 1", "#FF0000")
                with c_b:
                    color_2 = st.color_picker("Color 2", "#0000FF")
                color_hex = f"{color_1},{color_2}"
            else:
                color_hex = st.color_picker("Color Hex", "#000000")
                
            initial_weight = st.number_input("Initial Weight (g)", value=1000.0, step=100.0)
            price = st.number_input("Price ($)", value=24.99, step=1.0)
        
        submitted = st.form_submit_button("Add Filament")
        
        if submitted:
            payload = {
                "brand": brand,
                "material": material,
                "color_name": color_name,
                "color_hex": color_hex,
                "initial_weight": initial_weight,
                "remaining_weight": initial_weight,
                "price": price,
                "is_multicolor": is_multicolor 
            }
            try:
                res = requests.post(f"{API_URL}/filament", json=payload)
                if res.status_code == 200:
                    st.success(f"Added {brand} {material} successfully!")
                    st.cache_data.clear()
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

elif page == "Log Print":
    st.header("🖨️ Log a Print Job")
    
    filaments = get_filaments()
    filament_map = {f['id']: f for f in filaments}
    
    # Initialize assignment state
    if 'slot_assignments' not in st.session_state:
        st.session_state.slot_assignments = {}
    if 'active_slot_index' not in st.session_state:
        st.session_state.active_slot_index = 0
    
    tab1, tab2 = st.tabs(["📂 From File (Auto)", "✍️ Visual Selector (Manual)"])
    
    with tab1:
        st.info("Upload a .3mf or .gcode file to automatically extract filament usage.")
        uploaded_file = st.file_uploader("Choose a file", type=['gcode', '3mf'])
        
        if uploaded_file is not None:
            # Cache parse result
            if 'parse_result' not in st.session_state or st.session_state.get('last_uploaded_file') != uploaded_file.name:
                files = {"file": (uploaded_file.name, uploaded_file, "application/octet-stream")}
                try:
                    with st.spinner("Parsing file metadata..."):
                        res = requests.post(f"{API_URL}/parse-file", files=files)
                    
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.parse_result = data.get("estimated_weights_g", [])
                        st.session_state.last_uploaded_file = uploaded_file.name
                        # Reset assignments on new file
                        st.session_state.slot_assignments = {}
                        st.session_state.active_slot_index = 0
                    else:
                        st.session_state.parse_result = []
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.session_state.parse_result = []

            weights = st.session_state.parse_result
            
            if not weights:
                st.warning("No usage data found.")
            else:
                job_name = st.text_input("Job Name", value=uploaded_file.name)
                success = st.checkbox("Print Success?", value=True)
                
                st.divider()
                st.subheader("1. Select Slot to Assign")
                
                # Render Slot Targets (Horizontal)
                cols = st.columns(len(weights))
                for i, weight in enumerate(weights):
                    # Determine if this slot is 'active' or 'assigned'
                    is_active = (i == st.session_state.active_slot_index)
                    assigned_fid = st.session_state.slot_assignments.get(i)
                    
                    # Styling for the slot box
                    border_color = "#ff4b4b" if is_active else "#444"
                    bg_color = "#262730" if is_active else "#0e1117"
                    
                    assigned_text = "❌ Unassigned"
                    color_preview_style = "background-color: #333;"
                    
                    if assigned_fid and assigned_fid in filament_map:
                        f = filament_map[assigned_fid]
                        assigned_text = f"✅ {f['brand']} {f['color_name']}"
                        # Color Hex Logic
                        hex_code = f.get('color_hex', '#000000')
                        if "," in hex_code:
                            colors = hex_code.split(",")
                            color_preview_style = f"background: linear-gradient(45deg, {colors[0]} 50%, {colors[1]} 50%);"
                        else:
                            color_preview_style = f"background-color: {hex_code};"
                    
                    with cols[i]:
                        # Make it look like a card
                        st.markdown(
                            f"""
                            <div style="
                                border: 2px solid {border_color}; 
                                background-color: {bg_color};
                                border-radius: 8px; 
                                padding: 10px; 
                                text-align: center;
                                cursor: pointer;
                                margin-bottom: 10px;
                            ">
                                <div style="font-weight: bold; font-size: 1.1em;">Slot {i+1}</div>
                                <div style="font-size: 1.5em; margin: 5px 0;">{weight}g</div>
                                <div style="{color_preview_style} width: 100%; height: 10px; border-radius: 2px; margin: 5px 0;"></div>
                                <div style="font-size: 0.8em; color: #aaa;">{assigned_text}</div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                        
                        # Invisible button to handle selection
                        if st.button(f"Select Slot {i+1}", key=f"btn_slot_{i}", use_container_width=True):
                            st.session_state.active_slot_index = i
                            st.rerun()

                st.divider()
                st.subheader(f"2. Choose Filament for Slot {st.session_state.active_slot_index + 1}")
                
                # Render Filament Grid
                # 4 columns grid
                grid_cols = st.columns(4)
                
                for idx, f in enumerate(filaments):
                    col = grid_cols[idx % 4]
                    
                    # Prepare Color Style
                    hex_code = f.get('color_hex', '#000000')
                    if "," in hex_code:
                        colors = hex_code.split(",")
                        style = f"background: linear-gradient(45deg, {colors[0]} 50%, {colors[1]} 50%);"
                    else:
                        style = f"background-color: {hex_code};"
                    
                    with col:
                        # Visual Card
                        st.markdown(
                            f'<div style="{style} width: 100%; height: 20px; border-radius: 4px 4px 0 0; border: 1px solid #555;"></div>',
                            unsafe_allow_html=True
                        )
                        # Button
                        label = f"{f['brand']} - {f['color_name']}\n({f['material']})"
                        if st.button(label, key=f"pick_{f['id']}"):
                            # Assign
                            st.session_state.slot_assignments[st.session_state.active_slot_index] = f['id']
                            
                            # Auto-advance to next slot if available
                            if st.session_state.active_slot_index < len(weights) - 1:
                                st.session_state.active_slot_index += 1
                            st.rerun()
                
                st.divider()
                
                # Log Print Button
                # Check if all slots assigned
                all_assigned = len(st.session_state.slot_assignments) == len(weights)
                
                if st.button("Log Print Job", type="primary", disabled=not all_assigned):
                    usage_payload = []
                    for i, weight in enumerate(weights):
                        usage_payload.append({
                            "filament_id": st.session_state.slot_assignments[i],
                            "grams_used": weight
                        })
                    
                    print_data = {
                        "name": job_name,
                        "success": success,
                        "filaments_used": usage_payload
                    }
                    
                    try:
                        r = requests.post(f"{API_URL}/print", json=print_data)
                        if r.status_code == 200:
                            st.success("Print logged successfully!")
                            st.cache_data.clear()
                            # Clear state
                            st.session_state.slot_assignments = {}
                            st.session_state.active_slot_index = 0
                        else:
                            st.error(f"Error: {r.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
                
                if not all_assigned:
                    st.caption("Please assign a filament to all slots to enable logging.")

    with tab2:
        # New Visual Selection Logic - "Spreadsheet Style"
        st.subheader("Enter Grams for Used Filaments")
        st.caption("Scroll down and enter weight for any filament used. Leave at 0 if not used.")

        with st.form("bulk_manual_entry"):
            job_name = st.text_input("Job Name", value="Manual Print")
            success = st.checkbox("Success", value=True)
            
            st.divider()
            
            usage_inputs = {}

            for f in filaments:
                # Visual Color Box Logic
                color_hex = f.get('color_hex', '#000000')
                if "," in color_hex:
                    colors = color_hex.split(",")
                    bg_style = f"background: linear-gradient(45deg, {colors[0]} 50%, {colors[1]} 50%);"
                else:
                    bg_style = f"background-color: {color_hex};"
                
                c_viz, c_info, c_input = st.columns([1, 6, 3])
                
                with c_viz:
                    st.markdown(
                        f'<div style="{bg_style} width: 100%; height: 35px; border-radius: 5px; border: 1px solid #ccc;"></div>',
                        unsafe_allow_html=True
                    )
                
                with c_info:
                    st.write(f"**{f['brand']} {f['material']}**")
                    st.caption(f"{f['color_name']} (ID:{f['id']})")
                
                with c_input:
                    # Input for grams, default 0.0
                    val = st.number_input(
                        "Grams", 
                        min_value=0.0, 
                        step=1.0, 
                        key=f"bulk_w_{f['id']}", 
                        label_visibility="collapsed"
                    )
                    if val > 0:
                        usage_inputs[f['id']] = val
                
                st.divider()
            
            submit = st.form_submit_button("Log All Usage", type="primary")
            
            if submit:
                if not usage_inputs:
                    st.warning("No usage entered. Please enter grams for at least one filament.")
                else:
                    usage_payload = [
                        {"filament_id": fid, "grams_used": weight}
                        for fid, weight in usage_inputs.items()
                    ]
                    
                    payload = {
                        "name": job_name,
                        "success": success,
                        "filaments_used": usage_payload
                    }
                    
                    try:
                        r = requests.post(f"{API_URL}/print", json=payload)
                        if r.status_code == 200:
                            st.success(f"Logged print! Deducted from {len(usage_inputs)} spools.")
                            st.cache_data.clear()
                        else:
                            st.error(f"Error: {r.text}")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")

elif page == "Stats":
    st.header("📊 Statistics")
    try:
        res = requests.get(f"{API_URL}/stats")
        if res.status_code == 200:
            data = res.json()
            c1, c2 = st.columns(2)
            c1.metric("Plastic Used (This Month)", f"{data['total_plastic_used_this_month']:.2f}g")
            c2.metric("Most Used Color", data['most_used_color'])
        else:
            st.error("Could not fetch stats")
    except:
        st.error("Connection failed")