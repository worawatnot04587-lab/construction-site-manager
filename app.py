import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(layout="wide", page_title="Construction Management System")

# 2. ข้อมูลเริ่มต้น (Session State)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        "Task": ["Foundation", "Column Casting", "Wiring", "Painting"],
        "PIC": ["Manager", "Eng_A", "Eng_B", "Eng_A"],
        "Status": ["Completed", "On Track", "Pending", "Pending"],
        "Progress (%)": [100, 40, 0, 0],
        "Start": [datetime(2026, 4, 1), datetime(2026, 4, 10), datetime(2026, 4, 20), datetime(2026, 4, 25)],
        "End": [datetime(2026, 4, 9), datetime(2026, 4, 19), datetime(2026, 4, 24), datetime(2026, 5, 5)],
        "Photo": [None, None, None, None]
    })

# 3. Sidebar: ระบบ Login (จำลอง)
with st.sidebar:
    st.title("🔐 Login")
    user = st.selectbox("Select Role", ["Manager", "Eng_A", "Eng_B"])
    st.write("---")
    st.info(f"Logged in as: **{user}**")
    st.write("ระบบรายงานความคืบหน้างานก่อสร้าง")

st.title(f"🏗️ Construction Management System")
st.subheader(f"Welcome, {user}")

# 4. ส่วนแสดงผล Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Tasks", len(st.session_state.data))
col2.metric("Active Progress", f"{int(st.session_state.data['Progress (%)'].mean())}%")
col3.metric("Status", "Normal Operations")

# 5. Gantt Chart (แผนงานโครงการ)
st.subheader("📅 Project Timeline (Gantt Chart)")
fig = px.timeline(st.session_state.data, x_start="Start", x_end="End", y="Task", color="Status")
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)

# 6. ตารางจัดการงาน
st.subheader("📋 Task Editor")
edited_df = st.data_editor(st.session_state.data, use_container_width=True)
if st.button("💾 Save All Data"):
    st.session_state.data = edited_df
    st.success("บันทึกข้อมูลเรียบร้อย!")

# 7. ฟอร์มอัปเดตงาน (สำหรับ Engineer)
st.divider()
st.subheader("✏️ Update My Task (Proof of Work)")
my_tasks = st.session_state.data[st.session_state.data['PIC'] == user]

if not my_tasks.empty:
    with st.form("update_form"):
        task_select = st.selectbox("Select Task", my_tasks['Task'].tolist())
        new_progress = st.slider("Update Progress (%)", 0, 100, 20)
        new_status = st.selectbox("Update Status", ["On Track", "Delay", "Completed"])
        uploaded_file = st.file_uploader("Upload Image Proof", type=['jpg', 'png'])
        
        if st.form_submit_button("Submit Report"):
            idx = st.session_state.data[st.session_state.data['Task'] == task_select].index[0]
            st.session_state.data.at[idx, 'Progress (%)'] = new_progress
            st.session_state.data.at[idx, 'Status'] = new_status
            if uploaded_file:
                st.session_state.data.at[idx, 'Photo'] = uploaded_file.name
            st.success(f"Task '{task_select}' updated!")
            st.rerun()
else:
    st.write("คุณไม่มีงานที่รับผิดชอบในระบบ")

# 8. แสดงรูปผลงาน
st.subheader("🖼️ Proof Gallery")
cols = st.columns(3)
count = 0
for _, row in st.session_state.data.iterrows():
    if row['Photo']:
        with cols[count % 3]:
            st.write(f"Task: {row['Task']}")
            st.info(f"Attached: {row['Photo']}")
        count += 1
