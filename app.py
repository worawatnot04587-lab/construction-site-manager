import streamlit as st
import pandas as pd

# 1. ตั้งค่าข้อมูลเริ่มต้น
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "Task": ["Foundation", "Column Casting", "Wiring", "Painting"],
        "PIC": ["Eng_A", "Eng_B", "Eng_A", "Eng_C"],
        "Progress (%)": [80, 40, 0, 0],
        "Status": ["On Track", "Delay", "Pending", "Pending"]
    })

st.title("🏗️ Construction Management System")

# 2. ตารางแสดงสถานะ (ปรับให้ Status เป็น Dropdown)
st.subheader("📋 Task Overview")
edited_df = st.data_editor(
    st.session_state.df, 
    use_container_width=True,
    column_config={
        "Status": st.column_config.SelectboxColumn(
            "Status",
            options=["On Track", "Delay", "Pending", "Pass"],
            required=True,
        )
    }
)
st.session_state.df = edited_df

# 3. ส่วนฟอร์มอัปเดตงานและอัปโหลดรูป
st.divider()
st.subheader("✏️ Update Proof of Work")

with st.form("update_form"):
    col1, col2 = st.columns(2)
    with col1:
        task_select = st.selectbox("Select Task to Update", st.session_state.df["Task"])
    with col2:
        image_file = st.file_uploader("Upload Image Proof (JPG/PNG)", type=['png', 'jpg', 'jpeg'])
    
    submit_button = st.form_submit_button("Confirm Update")

    if submit_button:
        if image_file is not None:
            st.success(f"Successfully updated proof for: {task_select}")
            st.image(image_file, caption=f"Proof for {task_select}", width=300)
        else:
            st.warning("Please upload an image.")
