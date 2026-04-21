import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. ตั้งค่าหน้าจอ
st.set_page_config(layout="wide", page_title="Construction Management System")

# 2. Initialize Session State (ข้อมูลจะคงอยู่ขณะรันแอป)
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

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.current_role = None

# 3. Sidebar (ระบบ Login และจัดการบัญชี)
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
        
        # ฟังก์ชันเพิ่มวิศวกรใหม่ (เฉพาะ Manager)
        if st.session_state.current_role == "Manager":
            with st.expander("➕ เพิ่มวิศวกรใหม่"):
                new_user = st.text_input("ชื่อวิศวกร (ID)")
                new_pass = st.text_input("ตั้งรหัสผ่าน", type="password")
                if st.button("บันทึกวิศวกรใหม่"):
                    if new_user in st.session_state.passwords:
                        st.error("ชื่อนี้มีอยู่ในระบบแล้ว!")
                    else:
                        st.session_state.passwords[new_user] = new_pass
                        st.success(f"เพิ่ม {new_user} เรียบร้อย!")
        
        # เปลี่ยนรหัสตัวเอง
        with st.expander("⚙️ เปลี่ยนรหัสผ่านของตัวเอง"):
            old_pass = st.text_input("รหัสผ่านเดิม", type="password")
            new_pass = st.text_input("รหัสผ่านใหม่", type="password")
            if st.button("เปลี่ยนรหัส"):
                if old_pass == st.session_state.passwords[st.session_state.current_role]:
                    st.session_state.passwords[st.session_state.current_role] = new_pass
                    st.success("เปลี่ยนรหัสสำเร็จ!")
                else:
                    st.error("รหัสเดิมผิด")

        if st.button("ออกจากระบบ"):
            st.session_state.authenticated = False
            st.session_state.current_role = None
            st.rerun()

# 4. หน้าหลัก (แสดงตารางงานและกราฟตลอดเวลา)
st.title(f"🏗️ ระบบบริหารจัดการงานก่อสร้าง")

col1, col2, col3 = st.columns(3)
col1.metric("จำนวนงานทั้งหมด", len(st.session_state.data))
col2.metric("ความคืบหน้าเฉลี่ย", f"{int(st.session_state.data['Progress (%)'].mean())}%")
col3.metric("สถานะโครงการ", "ปกติ")

st.subheader("📅 แผนงานโครงการ (Gantt Chart)")
fig = px.timeline(st.session_state.data, x_start="Start", x_end="End", y="Task", color="Status")
fig.update_yaxes(autorange="reversed")
st.plotly_chart(fig, use_container_width=True)

# ตารางงาน (แสดงให้ทุกคนเห็น แต่ถ้าไม่ใช่ Manager อาจจะ lock ไม่ให้แก้ไขได้)
st.subheader("📋 ตารางข้อมูลงาน")
is_manager = st.session_state.current_role == "Manager"
edited_df = st.data_editor(st.session_state.data, use_container_width=True, num_rows="dynamic", disabled=not is_manager)

if is_manager and st.button("💾 บันทึกตาราง (เฉพาะ Manager)"):
    st.session_state.data = edited_df
    st.success("บันทึกข้อมูลเรียบร้อย!")
    st.rerun()

# 5. ส่วนอัปเดตงาน (แสดงเฉพาะคนที่ Login แล้ว)
st.divider()
st.subheader("✏️ อัปเดตงานที่รับผิดชอบ")

if not st.session_state.authenticated:
    st.info("👈 โปรด Login เพื่ออัปเดตสถานะงานของคุณ")
else:
    user = st.session_state.current_role
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

# 6. คลังรูปภาพ
st.subheader("🖼️ คลังรูปภาพผลงาน")
df_with_photos = st.session_state.data[st.session_state.data['Photo'].notna()]
if df_with_photos.empty:
    st.info("ยังไม่มีการอัปโหลดรูปภาพผลงาน")
else:
    # ... (โค้ดแสดงรูปภาพเหมือนเดิม)
    pass
