import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. ตั้งค่าหน้าจอ
st.set_page_config(layout="wide", page_title="Construction Management System")

# 2. Initialize Session State (ข้อมูลทั้งหมด)
if 'passwords' not in st.session_state:
    st.session_state.passwords = {"Manager": "1234", "Eng_A": "5555", "Eng_B": "9999"}

if 'data' not in st.session_state:
    today = datetime.today()
    st.session_state.data = pd.DataFrame({
        "Task": ["งานฐานราก", "งานหล่อเสา", "งานระบบไฟฟ้า", "งานสี"],
        "PIC": ["Manager", "Eng_A", "Eng_B", "Eng_A"],
        "Status": ["เสร็จสิ้น", "กำลังดำเนินการ", "รอเริ่มงาน", "รอเริ่มงาน"],
        "Progress (%)": [100, 40, 0, 0],
        "Start": [today, today + timedelta(days=7), today + timedelta(days=14), today + timedelta(days=21)],
        "End": [today + timedelta(days=6), today + timedelta(days=13), today + timedelta(days=20), today + timedelta(days=27)],
        "Photo": [None, None, None, None]
    })

if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Date", "Task", "PIC", "Progress (%)", "Status"])

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.current_role = None

# 3. Sidebar: ระบบ Login และจัดการบัญชี
with st.sidebar:
    st.title("🔐 ระบบจัดการ")
    if not st.session_state.authenticated:
        role = st.selectbox("เลือกบทบาทผู้ใช้งาน", list(st.session_state.passwords.keys()))
        password = st.text_input("รหัสผ่าน", type="password")
        if st.button("เข้าสู่ระบบ"):
            if st.session_state.passwords.get(role) == password:
                st.session_state.authenticated = True
                st.session_state.current_role = role
                st.rerun()
            else:
                st.error("รหัสผ่านไม่ถูกต้อง")
    else:
        st.success(f"ล็อกอินเป็น: **{st.session_state.current_role}**")
        if st.session_state.current_role == "Manager":
            with st.expander("➕ เพิ่มวิศวกร"):
                new_user = st.text_input("ชื่อ (ID)")
                new_pass = st.text_input("รหัสผ่าน", type="password")
                if st.button("บันทึก"):
                    st.session_state.passwords[new_user] = new_pass
                    st.rerun()
        if st.button("ออกจากระบบ"):
            st.session_state.authenticated = False
            st.session_state.current_role = None
            st.rerun()

# 4. หน้าหลัก (Main Page)
st.title("🏗️ ระบบบริหารจัดการงานก่อสร้าง")

# Dashboard Metrics
col1, col2, col3 = st.columns(3)
col1.metric("จำนวนงานทั้งหมด", len(st.session_state.data))
col2.metric("ความคืบหน้าเฉลี่ย", f"{int(st.session_state.data['Progress (%)'].mean())}%")
col3.metric("สถานะโครงการ", "ปกติ")

st.subheader("📅 แผนงานโครงการ (Gantt Chart)")
fig = px.timeline(st.session_state.data, x_start="Start", x_end="End", y="Task", color="Status")
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)

# ตารางแก้ไขข้อมูล (Manager เท่านั้น)
st.subheader("📋 ตารางข้อมูลงานทั้งหมด")
if st.session_state.current_role == "Manager":
    st.session_state.data = st.data_editor(st.session_state.data, use_container_width=True, num_rows="dynamic")
else:
    st.dataframe(st.session_state.data, use_container_width=True)

# 5. ส่วนอัปเดตงาน (สำหรับทุกคนที่ Login)
st.divider()
st.subheader("✏️ อัปเดตสถานะงานประจำวัน")

if not st.session_state.authenticated:
    st.info("👈 โปรด Login เพื่ออัปเดตสถานะงานของคุณ")
else:
    user = st.session_state.current_role
    # เลือกงาน (ถ้าเป็น Manager เห็นหมด, วิศวกรเห็นของตัวเอง)
    if user == "Manager":
        task_options = st.session_state.data['Task'].tolist()
    else:
        task_options = st.session_state.data[st.session_state.data['PIC'] == user]['Task'].tolist()

    if task_options:
        with st.form("update_form"):
            task_select = st.selectbox("เลือกงานที่ต้องการอัปเดต", task_options)
            
            # ดึงค่าปัจจุบันมาเป็น Default ใน Slider
            current_idx = st.session_state.data[st.session_state.data['Task'] == task_select].index[0]
            current_val = int(st.session_state.data.at[current_idx, 'Progress (%)'])
            
            new_progress = st.slider("ความคืบหน้า (%)", 0, 100, current_val)
            new_status = st.selectbox("สถานะปัจจุบัน", ["กำลังดำเนินการ", "ล่าช้า", "เสร็จสิ้น"])
            uploaded_file = st.file_uploader("อัปโหลดรูปภาพ", type=['jpg', 'png', 'jpeg'])
            
            if st.form_submit_button("บันทึกรายงานความคืบหน้า"):
                # อัปเดตตารางหลัก
                st.session_state.data.at[current_idx, 'Progress (%)'] = new_progress
                st.session_state.data.at[current_idx, 'Status'] = new_status
                if uploaded_file:
                    st.session_state.data.at[current_idx, 'Photo'] = uploaded_file.name
                
                # บันทึก History
                new_log = pd.DataFrame({
                    "Date": [datetime.now().strftime("%Y-%m-%d %H:%M")],
                    "Task": [task_select],
                    "PIC": [user],
                    "Progress (%)": [new_progress],
                    "Status": [new_status]
                })
                st.session_state.history = pd.concat([st.session_state.history, new_log], ignore_index=True)
                st.success(f"บันทึกงาน '{task_select}' เรียบร้อย!")
                st.rerun()
    else:
        st.warning("คุณไม่มีงานที่รับผิดชอบในขณะนี้")

# 6. แสดงประวัติการอัปเดตและรูปภาพ
st.divider()
tab1, tab2 = st.tabs(["📅 ประวัติการอัปเดต (Logs)", "🖼️ คลังรูปภาพ"])

with tab1:
    if not st.session_state.history.empty:
        st.dataframe(st.session_state.history.sort_values(by="Date", ascending=False), use_container_width=True)
    else:
        st.write("ยังไม่มีข้อมูลประวัติการอัปเดต")

with tab2:
    df_with_photos = st.session_state.data[st.session_state.data['Photo'].notna()]
    if not df_with_photos.empty:
        for _, row in df_with_photos.iterrows():
            st.write(f"**งาน:** {row['Task']} | **อัปเดตโดย:** {row['PIC']} | **ไฟล์:** {row['Photo']}")
    else:
        st.write("ยังไม่มีการอัปโหลดรูปภาพ")
