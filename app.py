import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(layout="wide", page_title="Construction Management System")

# 2. ข้อมูลเริ่มต้น (Session State)
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        "Task": ["งานฐานราก", "งานหล่อเสา", "งานระบบไฟฟ้า", "งานสี"],
        "PIC": ["Manager", "Eng_A", "Eng_B", "Eng_A"],
        "Status": ["เสร็จสิ้น", "กำลังดำเนินการ", "รอเริ่มงาน", "รอเริ่มงาน"],
        "Progress (%)": [100, 40, 0, 0],
        "Start": [datetime(2026, 4, 1), datetime(2026, 4, 10), datetime(2026, 4, 20), datetime(2026, 4, 25)],
        "End": [datetime(2026, 4, 9), datetime(2026, 4, 19), datetime(2026, 4, 24), datetime(2026, 5, 5)],
        "Photo": [None, None, None, None]
    })

# 3. Sidebar: ระบบ Login
with st.sidebar:
    st.title("🔐 เข้าสู่ระบบ")
    user = st.selectbox("เลือกบทบาทผู้ใช้งาน", ["Manager", "Eng_A", "Eng_B"])
    st.write("---")
    st.info(f"ผู้ใช้งานปัจจุบัน: **{user}**")
    st.caption("ระบบบริหารจัดการโครงการก่อสร้าง")

st.title(f"🏗️ ระบบบริหารจัดการงานก่อสร้าง")
st.subheader(f"สวัสดีคุณ, {user}")

# 4. ส่วนแสดงผล Metrics
col1, col2, col3 = st.columns(3)
col1.metric("จำนวนงานทั้งหมด", len(st.session_state.data))
col2.metric("ความคืบหน้าเฉลี่ย", f"{int(st.session_state.data['Progress (%)'].mean())}%")
col3.metric("สถานะโครงการ", "ปกติ")

# 5. Gantt Chart
st.subheader("📅 แผนงานโครงการ (Gantt Chart)")
fig = px.timeline(st.session_state.data, x_start="Start", x_end="End", y="Task", color="Status")
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)

# 6. ตารางจัดการงาน
st.subheader("📋 ตารางแก้ไขข้อมูลงาน")
edited_df = st.data_editor(st.session_state.data, use_container_width=True)
if st.button("💾 บันทึกข้อมูลทั้งหมด"):
    st.session_state.data = edited_df
    st.success("บันทึกข้อมูลเรียบร้อยแล้ว!")

# 7. ฟอร์มอัปเดตงาน (สำหรับ Engineer)
st.divider()
st.subheader("✏️ อัปเดตงานที่รับผิดชอบ")
my_tasks = st.session_state.data[st.session_state.data['PIC'] == user]

if not my_tasks.empty:
    with st.form("update_form"):
        task_select = st.selectbox("เลือกชื่องานที่ต้องการอัปเดต", my_tasks['Task'].tolist())
        new_progress = st.slider("ความคืบหน้า (%)", 0, 100, 20)
        new_status = st.selectbox("สถานะปัจจุบัน", ["กำลังดำเนินการ", "ล่าช้า", "เสร็จสิ้น"])
        uploaded_file = st.file_uploader("อัปโหลดรูปภาพผลงาน", type=['jpg', 'png', 'jpeg'])
        
        if st.form_submit_button("บันทึกรายงานความคืบหน้า"):
            idx = st.session_state.data[st.session_state.data['Task'] == task_select].index[0]
            st.session_state.data.at[idx, 'Progress (%)'] = new_progress
            st.session_state.data.at[idx, 'Status'] = new_status
            if uploaded_file:
                st.session_state.data.at[idx, 'Photo'] = uploaded_file.name
            st.success(f"บันทึกงาน '{task_select}' เรียบร้อย!")
            st.rerun()
else:
    st.warning("คุณไม่มีงานที่รับผิดชอบในระบบ ณ ขณะนี้")

# 8. แสดงรูปผลงาน
st.subheader("🖼️ คลังรูปภาพผลงาน")
cols = st.columns(3)
count = 0
for _, row in st.session_state.data.iterrows():
    if row['Photo']:
        with cols[count % 3]:
            st.write(f"**งาน:** {row['Task']}")
            st.info(f"ไฟล์: {row['Photo']}")
        count += 1
if count == 0:
    st.caption("ยังไม่มีการอัปโหลดรูปภาพผลงาน")
