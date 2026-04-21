import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# 1. ตั้งค่าหน้าจอ
st.set_page_config(layout="wide", page_title="Construction Management System")

# 2. ข้อมูลเริ่มต้น (ตั้งค่าวันที่ตามปัจจุบัน)
today = datetime.today()

if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame({
        "Task": ["งานฐานราก", "งานหล่อเสา", "งานระบบไฟฟ้า", "งานสี"],
        "PIC": ["Manager", "Eng_A", "Eng_B", "Eng_A"],
        "Status": ["เสร็จสิ้น", "กำลังดำเนินการ", "รอเริ่มงาน", "รอเริ่มงาน"],
        "Progress (%)": [100, 40, 0, 0],
        # คำนวณวันที่ให้อิงจากวันนี้
        "Start": [today, today + timedelta(days=7), today + timedelta(days=14), today + timedelta(days=21)],
        "End": [today + timedelta(days=6), today + timedelta(days=13), today + timedelta(days=20), today + timedelta(days=27)],
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
    st.rerun()

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

# 8. แสดงรูปผลงาน (จัดกลุ่มตามหมวดงาน)
st.subheader("🖼️ คลังรูปภาพผลงาน")
df_with_photos = st.session_state.data[st.session_state.data['Photo'].notna()]

if df_with_photos.empty:
    st.info("ยังไม่มีการอัปโหลดรูปภาพผลงานในขณะนี้")
else:
    grouped = df_with_photos.groupby('Task')
    for task_name, group_data in grouped:
        with st.expander(f"📦 หมวดงาน: {task_name}", expanded=True):
            for _, row in group_data.iterrows():
                col_left, col_right = st.columns([1, 2])
                with col_left:
                    st.image("https://via.placeholder.com/150", caption="ภาพถ่ายหน้างาน") 
                with col_right:
                    st.write(f"**สถานะ:** {row['Status']}")
                    st.write(f"**ผู้รับผิดชอบ (PIC):** 👤 {row['PIC']}")
                    st.success(f"ไฟล์ที่แนบ: {row['Photo']}")
            st.divider()
