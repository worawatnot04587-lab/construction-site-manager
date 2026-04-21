import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(layout="wide", page_title="Construction Daily Log")

# 2. Initialize Session State
if 'passwords' not in st.session_state:
    st.session_state.passwords = {"Manager": "1234", "Eng_A": "5555", "Eng_B": "9999"}

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        "Task": ["งานฐานราก", "งานหล่อเสา", "งานระบบไฟฟ้า", "งานสี"],
        "PIC": ["Manager", "Eng_A", "Eng_B", "Eng_A"],
        "Status": ["เสร็จสิ้น", "กำลังดำเนินการ", "รอเริ่มงาน", "รอเริ่มงาน"],
        "Progress (%)": [100, 40, 0, 0],
        "Photo": [None, None, None, None]
    })

# เก็บประวัติการอัปเดต
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Date", "Task", "PIC", "Progress (%)", "Status"])

if 'authenticated' not in st.session_state:
    st.authenticated = False
    st.session_state.current_role = None

# --- Sidebar และ UI อื่นๆ เหมือนเดิม ---
# (ย่อโค้ดส่วน Login ไว้เพื่อให้ดูส่วนการอัปเดตชัดๆ)
with st.sidebar:
    # ... ระบบ Login และเพิ่มวิศวกรเหมือนเดิม ...
    pass

st.title("🏗️ ระบบอัปเดตงานรายวัน")

# ตารางหลัก (สถานะปัจจุบัน)
st.subheader("📋 สถานะงานปัจจุบัน (Current Status)")
st.dataframe(st.session_state.data, use_container_width=True)

# 3. ส่วนอัปเดตงาน (จุดที่เพิ่ม Log)
st.divider()
st.subheader("✏️ อัปเดตสถานะงานประจำวัน")

if st.session_state.get('authenticated'):
    user = st.session_state.current_role
    my_tasks = st.session_state.data[st.session_state.data['PIC'] == user]
    
    if not my_tasks.empty:
        with st.form("daily_update"):
            task_select = st.selectbox("เลือกงาน", my_tasks['Task'].tolist())
            new_progress = st.slider("ความคืบหน้า (%)", 0, 100, int(st.session_state.data.loc[st.session_state.data['Task'] == task_select, 'Progress (%)'].values[0]))
            new_status = st.selectbox("สถานะ", ["กำลังดำเนินการ", "ล่าช้า", "เสร็จสิ้น"])
            
            if st.form_submit_button("บันทึกข้อมูลวันนี้"):
                today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 1. อัปเดตตารางหลัก
                idx = st.session_state.data[st.session_state.data['Task'] == task_select].index[0]
                st.session_state.data.at[idx, 'Progress (%)'] = new_progress
                st.session_state.data.at[idx, 'Status'] = new_status
                
                # 2. บันทึกลง History (Log)
                new_log = pd.DataFrame({
                    "Date": [today],
                    "Task": [task_select],
                    "PIC": [user],
                    "Progress (%)": [new_progress],
                    "Status": [new_status]
                })
                st.session_state.history = pd.concat([st.session_state.history, new_log], ignore_index=True)
                
                st.success(f"บันทึกข้อมูลของวันที่ {today} เรียบร้อย!")
                st.rerun()
    else:
        st.warning("คุณไม่มีงานที่รับผิดชอบ")
else:
    st.info("กรุณา Login เพื่อเริ่มอัปเดตงาน")

# 4. แสดงประวัติการอัปเดต (Daily Log)
st.divider()
st.subheader("📅 ประวัติการอัปเดตงาน (Daily Update Logs)")
if not st.session_state.history.empty:
    st.dataframe(st.session_state.history.sort_values(by="Date", ascending=False), use_container_width=True)
else:
    st.write("ยังไม่มีประวัติการอัปเดต")
