import streamlit as st
import pandas as pd
import io

# --- 1. PAGE CONFIG & BRANDING ---
st.set_page_config(page_title="Synapse State | PBL Engine", layout="wide", page_icon="🏃‍♂️")

# Custom CSS for a clean, professional dashboard look
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
    """, unsafe_allow_code=True)

# --- 2. THE SIDEBAR (Control Center) ---
with st.sidebar:
    # Pulling your specific logo from GitHub
    try:
        st.image("logo-black-web.png", use_container_width=True)
    except:
        st.title("Synapse State")
    
    st.divider()
    st.header("Upload Center")
    uploaded_file = st.file_uploader("Drop Workout CSV/TXT", type=["csv", "txt"])
    st.caption("The engine will automatically scan for your split times.")
    st.divider()
    st.markdown("Developed by **Mr. Dickens** | *stemandfitness.com*")

# --- 3. MAIN DASHBOARD LOGIC ---
if uploaded_file is not None:
    raw_csv_data = uploaded_file.getvalue().decode("utf-8")
    
    # Universal Data Sorter (Prevents the EmptyDataError)
    lines = raw_csv_data.strip().split('\n')
    split_index = None
    
    for i, line in enumerate(lines):
        if "Split" in line and "Time" in line:
            split_index = i
            break

    # Read the data safely, skipping messy rows
    if split_index is not None:
        splits_text = '\n'.join(lines[split_index:])
        df_splits = pd.read_csv(io.StringIO(splits_text), on_bad_lines='skip')
    else:
        df_splits = pd.read_csv(io.StringIO(raw_csv_data), on_bad_lines='skip')

    # Ensure the required columns exist before doing math
    if 'Time' in df_splits.columns:
        
        # Time processing logic
        def time_to_seconds(time_str):
            try:
                parts = str(time_str).split(':')
                return int(parts[0]) * 60 + int(parts[1]) if len(parts) == 2 else 0
            except: 
                return 0

        # Physics Calculations
        df_splits['Seconds'] = df_splits['Time'].apply(time_to_seconds)
        
        # Filter out rows where time didn't calculate properly to avoid dividing by zero
        df_splits = df_splits[df_splits['Seconds'] > 0].copy()
        
        runner_mass_kg = 75 
        df_splits['Velocity_m_s'] = 1000 / df_splits['Seconds']
        df_splits['Kinetic_Energy_J'] = 0.5 * runner_mass_kg * (df_splits['Velocity_m_s'] ** 2)

        # --- 4. BEAUTIFUL UI ---
        st.title("🏃‍♂️ Biometric Performance Analysis")
        st.markdown("Transforming raw endurance data into mathematical modeling sandboxes.")
        
        # Top Metric Row
        col1, col2, col3 = st.columns(3)
        avg_vel = df_splits['Velocity_m_s'].mean()
        max_ke = df_splits['Kinetic_Energy_J'].max()
        total_km = len(df_splits)
        
        col1.metric("Average Velocity", f"{avg_vel:.2f} m/s")
        col2.metric("Peak Kinetic Energy", f"{max_ke:.0f} J")
        col3.metric("Total Distance", f"{total_km} KM")

        st.divider()

        # Content Tabs
        tab1, tab2 = st.tabs(["📊 Data Visualization", "📝 PBL Lesson Generator"])

        with tab1:
            c1, c2 = st.columns([1.5, 1]) # Makes the chart wider than the table
            with c1:
                st.subheader("Velocity Trend over Distance")
                if 'KM' in df_splits.columns:
                    st.line_chart(df_splits.set_index('KM')['Velocity_m_s'])
                else:
                    st.line_chart(df_splits['Velocity_m_s'])
            with c2:
                st.subheader("Raw Kinematics Table")
                # Show only the most relevant columns if they exist
                display_cols = [col for col in ['KM', 'Time', 'Velocity_m_s', 'Kinetic_Energy_J'] if col in df_splits.columns]
                st.dataframe(df_splits[display_cols], use_container_width=True)

        with tab2:
            st.header("Culturally Responsive Module")
            st.markdown("Generate a custom classroom module based on the athlete's most severe fatigue point.")
            
            if st.button("🚀 Generate Physics Lesson", type="primary"):
                hardest_point = df_splits.loc[df_splits['Velocity_m_s'].idxmin()]
                
                # Check if KM exists, otherwise just use the row index
                km_marker = int(hardest_point['KM']) if 'KM' in hardest_point else "the hardest stretch"
                min_vel = hardest_point['Velocity_m_s']
                min_ke = hardest_point['Kinetic_Energy_J']
                
                st.success("Module Generated Successfully!")
                
                st.markdown(f"""
                ### **Module Title: The Physics of Fatigue**
                
                **Context:** An athlete running a local marathon in Doha hits a severe fatigue point at **Kilometer {km_marker}** due to glycogen depletion and local heat.
                
                **The Data:** At this exact moment, their velocity dropped to **{min_vel:.2f} m/s**, reducing their kinetic energy output to **{min_ke:.0f} Joules** per step.
                
                **Student Task (Kinematics & Biology):** 1. Assuming the runner's mass is 75kg, calculate the exact percentage drop in kinetic energy compared to their starting pace. 
                2. Using principles of human energy systems, explain how the body attempts to compensate for this mechanical loss, and propose a specific hydration or nutrition intervention.
                """)
    else:
        st.error("Error: Could not find a 'Time' column in this file. Please ensure your data includes lap/split times.")

else:
    # Hero Section when no file is uploaded
    st.title("Welcome to the Biometric Engine")
    st.markdown("Upload a CSV or TXT file in the sidebar to power up the engine.")
    # A great placeholder image of runners
    st.image("https://images.unsplash.com/photo-1530143311094-34d807799e8f?auto=format&fit=crop&q=80&w=1200", use_container_width=True)
