import streamlit as st
import pandas as pd
import io

# --- 1. PAGE CONFIG & BRANDING ---
st.set_page_config(page_title="STEM & Fitness | PBL Engine", layout="wide", page_icon="🏃‍♂️")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
    }
    </style>
    """, unsafe_allow_html=True)

with st.sidebar:
    try:
        st.image("logo-black-web.png", use_container_width=True)
    except:
        st.title("STEM & Fitness")
    st.divider()
    st.header("Upload Center")
    uploaded_file = st.file_uploader("Drop Workout CSV/TXT", type=["csv", "txt"])
    st.divider()
    st.markdown("Developed by **Mr. Dickens** | *stemandfitness.com*")

if uploaded_file is not None:
    # 1. READ THE FILE (Bulletproof Method)
    raw_csv_data = uploaded_file.getvalue().decode("utf-8")
    
    try:
        # We let pandas figure out if it uses commas, tabs, or spaces
        df_raw = pd.read_csv(io.StringIO(raw_csv_data), sep=None, engine='python', on_bad_lines='skip')
        df_raw.columns = df_raw.columns.astype(str).str.strip()
    except Exception as e:
        st.error(f"Could not read the file format. Please ensure it is a standard table. Error: {e}")
        st.stop()

    # 2. AUTO-DETECT COLUMNS OR ASK USER
    time_col = None
    km_col = None

    # Try to auto-guess the names
    for col in df_raw.columns:
        if 'time' in col.lower() or 'duration' in col.lower() or 'pace' in col.lower():
            time_col = col
        if 'km' in col.lower() or 'dist' in col.lower() or 'split' in col.lower():
            km_col = col

    # If the file has weird names and we can't guess, trigger the Manual UI
    if not time_col or not km_col:
        st.warning("Could not automatically detect the Time or Distance columns. Please select them below.")
        st.write("Here is a preview of your file:")
        st.dataframe(df_raw.head(3)) 
        
        c1, c2 = st.columns(2)
        with c1:
            km_col = st.selectbox("Which column is Distance/KM?", options=["Select..."] + list(df_raw.columns), index=0)
        with c2:
            time_col = st.selectbox("Which column is Time?", options=["Select..."] + list(df_raw.columns), index=0)

    # 3. IF COLUMNS ARE SET, RUN THE ENGINE
    if km_col != "Select..." and time_col != "Select..." and km_col and time_col:
        df_splits = df_raw.copy()
        
        def time_to_seconds(time_str):
            try:
                parts = str(time_str).strip().split(':')
                if len(parts) == 3: return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
                elif len(parts) == 2: return int(parts[0]) * 60 + float(parts[1])
                return float(time_str) 
            except: return 0

        df_splits['Seconds'] = df_splits[time_col].apply(time_to_seconds)
        df_splits = df_splits[df_splits['Seconds'] > 0].copy()
        
        runner_mass_kg = 75 
        df_splits['Velocity_m_s'] = 1000 / df_splits['Seconds']
        df_splits['Kinetic_Energy_J'] = 0.5 * runner_mass_kg * (df_splits['Velocity_m_s'] ** 2)

        # --- 4. DASHBOARD UI ---
        st.title("🏃‍♂️ Biometric Performance Analysis")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Average Velocity", f"{df_splits['Velocity_m_s'].mean():.2f} m/s")
        col2.metric("Peak Kinetic Energy", f"{df_splits['Kinetic_Energy_J'].max():.0f} J")
        col3.metric("Total Distance", f"{len(df_splits)} KM")

        st.divider()
        tab1, tab2 = st.tabs(["📊 Data Visualization", "📝 PBL Lesson Generator"])

        with tab1:
            c1, c2 = st.columns([1.5, 1])
            with c1:
                st.subheader("Velocity Trend over Distance")
                st.line_chart(df_splits.set_index(km_col)['Velocity_m_s'])
            with c2:
                st.subheader("Raw Kinematics Table")
                display_cols = [km_col, time_col, 'Velocity_m_s', 'Kinetic_Energy_J']
                st.dataframe(df_splits[display_cols], use_container_width=True)

        with tab2:
            st.header("Culturally Responsive Module")
            if st.button("🚀 Generate Physics Lesson", type="primary"):
                hardest_point = df_splits.loc[df_splits['Velocity_m_s'].idxmin()]
                km_marker = hardest_point[km_col]
                min_vel = hardest_point['Velocity_m_s']
                min_ke = hardest_point['Kinetic_Energy_J']
                
                st.success("Module Generated Successfully!")
                st.markdown(f"""
                ### **Module Title: The Physics of Fatigue**
                **Context:** An athlete running a local marathon in Doha hits a severe fatigue point at **Kilometer {km_marker}** due to glycogen depletion and local heat.
                **The Data:** At this exact moment, their velocity dropped to **{min_vel:.2f} m/s**, reducing their kinetic energy output to **{min_ke:.0f} Joules** per step.
                **Student Task (Kinematics & Biology):** 1. Assuming the runner's mass is 75kg, calculate the exact percentage drop in kinetic energy compared to their starting pace. 2. Using principles of human energy systems, explain how the body attempts to compensate for this mechanical loss, and propose a specific hydration or nutrition intervention.
                """)
else:
    st.title("Welcome to the Biometric Engine")
    st.markdown("Upload a CSV or TXT file in the sidebar to power up the engine.")
    st.image("https://images.unsplash.com/photo-1530143311094-34d807799e8f?auto=format&fit=crop&q=80&w=1200", use_container_width=True)
