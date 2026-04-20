import streamlit as st
import pandas as pd
import plotly.express as px

# ตั้งค่า App
st.set_page_config(page_title="ConstruFlow", layout="wide")

# สร้างข้อมูลจำลอง (Database)
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        'Task': ['Foundation', 'Column Casting', 'Wiring', 'Painting'],
        'PIC': ['Eng_A', 'Eng_B', 'Eng_A', 'Eng_C'],
        'Progress': [80, 40, 0, 0],
        'QC': ['Pass', 'Pending', 'Pending', 'Pending']
    })

# ระบบ Login (Access Control)
st.sidebar.title("Login System")
user = st.sidebar.selectbox("Select User", ["Manager", "Eng_A", "Eng_B", "Eng_C"])
st.sidebar.info(f"Logged in as: {user}")

st.title(f"Construction Management System - Welcome {user}")

# กรองงานตาม User
if user == "Manager":
    df_view = st.session_state.df
else:
    df_view = st.session_state.df[st.session_state.df['PIC'] == user]

# หน้าแสดงงานและแก้ไขงาน
st.subheader("📋 Task List & Progress Update")
edited_df = st.data_editor(df_view, use_container_width=True)

# อัปเดตข้อมูลกลับเข้า Session State
if st.button("Save Changes"):
    if user == "Manager":
        st.session_state.df = edited_df
    else:
        st.session_state.df.update(edited_df)
    st.success("Data Saved!")

# ระบบ Dashboard & Alert (เฉพาะ Manager)
if user == "Manager":
    st.divider()
    st.subheader("📊 Project Analytics")
    
    st.session_state.df['Status'] = st.session_state.df['Progress'].apply(lambda x: "Delay" if x < 50 else "On Track")
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(st.session_state.df, x='Task', y='Progress', color='Status', title="Project Progress")
        st.plotly_chart(fig)
    with col2:
        st.subheader("⚠️ Alerts")
        delay_tasks = st.session_state.df[st.session_state.df['Status'] == 'Delay']
        if not delay_tasks.empty:
            st.warning(f"Tasks behind schedule: {delay_tasks['Task'].tolist()}")
        else:
            st.success("All tasks on schedule.")
