import streamlit as st
import pandas as pd
import io

# Set up the webpage visuals first
st.set_page_config(page_title="PBL Engine", layout="wide")
st.title("🏃‍♂️ The Biometric PBL Engine")
st.markdown("Transforming athletic performance into mathematical modeling sandboxes.")

# --- THE NEW UPLOADER ---
# This creates the drag-and-drop box on your website
uploaded_file = st.file_uploader("Drop your workout data file here (CSV or TXT)", type=["csv", "txt"])

# The engine will ONLY run if a file has been uploaded
if uploaded_file is not None:
    
    # 1. Read the uploaded file and decode it into text Python can read
    raw_csv_data = uploaded_file.getvalue().decode("utf-8")
    
    # 2. The Data Sorting Logic (Same as before)
    lines = raw_csv_data.strip().split('\n')
    split_index = 0
    for i, line in enumerate(lines):
        if line.startswith("Split,KM,Time"):
            split_index = i
            break

    summary_text = '\n'.join(lines[:split_index])
    splits_text = '\n'.join(lines[split_index:])

    df_summary = pd.read_csv(io.StringIO(summary_text))
    df_splits = pd.read_csv(io.StringIO(splits_text))

    def time_to_seconds(time_str):
        parts = time_str.split(':')
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        return 0

    df_splits['Seconds'] = df_splits['Time'].apply(time_to_seconds)

    # --- 3. THE PHYSICS CALCULATOR ---
    runner_mass_kg = 75 
    df_splits['Distance_m'] = 1000 
    df_splits['Velocity_m_s'] = df_splits['Distance_m'] / df_splits['Seconds']
    df_splits['Kinetic_Energy_Joules'] = 0.5 * runner_mass_kg * (df_splits['Velocity_m_s'] ** 2)

    # --- 4. THE FRONT-END DASHBOARD ---
    st.header("1. Core Kinematics & Energy")
    st.markdown("This table calculates the exact velocity and kinetic energy required for each kilometer.")
    st.dataframe(df_splits[['KM', 'Time', 'Velocity_m_s', 'Kinetic_Energy_Joules']], use_container_width=True)

    st.header("2. Velocity Curve Visualization")
    st.markdown("Visualizing the runner's speed over the course of the session.")
    st.line_chart(df_splits.set_index('KM')['Velocity_m_s'])

    st.divider()

    st.header("3. Culturally Responsive PBL Generator")
    st.markdown("Turn this specific dataset into an actionable classroom module.")

    if st.button("Generate Physics Module", type="primary"):
        hardest_km = df_splits.loc[df_splits['Velocity_m_s'].idxmin()]
        km_marker = int(hardest_km['KM'])
        min_vel = hardest_km['Velocity_m_s']
        min_ke = hardest_km['Kinetic_Energy_Joules']
        
        st.success("Module Generated Successfully!")
        
        with st.expander("📝 View Generated Word Problem", expanded=True):
            st.markdown(f"**Context:** An athlete running a local marathon hits a severe fatigue point at **Kilometer {km_marker}** due to local heat and glycogen depletion.")
            st.markdown(f"**The Data:** At this exact kilometer, their velocity drops to **{min_vel:.2f} m/s**, reducing their kinetic energy output to **{min_ke:.2f} Joules** per step.")
            st.markdown("**Student Task (Kinematics):** If the runner's mass is 75kg, calculate the exact percentage drop in kinetic energy compared to their starting pace at Kilometer 1. How does the body's energy system shift to compensate for this mechanical loss?")
            
        with st.expander("🤖 AI Teacher Prompt (Copy/Paste)"):
            st.info(f"Act as a master STEM teacher. I have a student analyzing a marathon runner. At kilometer {km_marker}, the runner's velocity is {min_vel:.2f} m/s and kinetic energy is {min_ke:.2f} J. Create a 3-part project-based learning activity focusing on biomechanics, human energy systems, and mathematical modeling based on this exact data point.")

else:
    # This message shows up when the page first loads and no file is present
    st.info("👆 Please upload a workout file to power up the engine.")
