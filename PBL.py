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
    uploaded_file = st.file_uploader("Drop Workout Summary CSV", type=["csv", "txt"])
    st.divider()
    st.markdown("Developed by **Mr. Dickens** | *stemandfitness.com*")

if uploaded_file is not None:
    raw_csv_data = uploaded_file.getvalue().decode("utf-8")

    # 1. READ THE SUMMARY DATA
    try:
        df = pd.read_csv(io.StringIO(raw_csv_data), sep=',', on_bad_lines='skip')
        df.columns = df.columns.str.strip()
    except Exception as e:
        st.error(f"Could not read file. Error: {e}")
        st.stop()

    # 2. CHECK IF IT IS A SUMMARY FILE
    if 'Metric' in df.columns and 'Value' in df.columns:
        
        def get_val(metric_name):
            try:
                val = str(df.loc[df['Metric'] == metric_name, 'Value'].values[0])
                val_clean = ''.join(c for c in val if c.isdigit() or c == '.')
                return float(val_clean) if val_clean else 0.0
            except:
                return 0.0

        # Extract Core Metrics
        distance = get_val('Distance')
        calories = get_val('Total Calories')
        avg_speed_kmh = get_val('Average Speed')
        cadence = get_val('Average Cadence')
        stride_cm = get_val('Average Stride Length')

        # Baseline Conversions
        avg_speed_ms = avg_speed_kmh / 3.6
        stride_m = stride_cm / 100
        total_joules = calories * 4184 

        # --- 3. DASHBOARD UI ---
        st.title("🏃‍♂️ Biometric Performance Analysis")
        st.markdown("Transforming summary endurance data into mathematical modeling sandboxes.")

        # Top Baseline Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Distance", f"{distance:.2f} km")
        col2.metric("Average Speed", f"{avg_speed_ms:.2f} m/s")
        col3.metric("Total Energy Expended", f"{calories:.0f} kcal")

        st.divider()

        # The Three Core Features
        tab1, tab2, tab3 = st.tabs(["🎛️ Interactive Simulator", "📝 PBL Lesson & Export", "📊 Raw Data"])

        with tab1:
            st.header("Kinematics & Thermodynamics Sandbox")
            st.markdown("Adjust the variables below to see how physical and environmental factors alter the mathematical model of the run.")
            
            c1, c2 = st.columns([1, 2])
            with c1:
                st.subheader("Set Variables")
                sim_mass = st.slider("Runner Mass (kg)", min_value=40, max_value=120, value=75, step=1)
                sim_temp = st.slider("Ambient Temperature (°C)", min_value=10, max_value=45, value=25, step=1)
            
            with c2:
                st.subheader("Live Physics Output")
                # Dynamic Math based on sliders
                sim_ke = 0.5 * sim_mass * (avg_speed_ms ** 2)
                
                # A basic thermodynamic modifier (simulating 2% more energy cost per degree over 15C)
                temp_penalty = 1.0 if sim_temp <= 15 else 1.0 + ((sim_temp - 15) * 0.02)
                sim_joules_adjusted = total_joules * temp_penalty * (sim_mass / 75.0) # Scaled by mass and temp
                
                sc1, sc2 = st.columns(2)
                sc1.metric("Live Kinetic Energy", f"{sim_ke:.0f} Joules", delta="Calculated from Mass & Speed", delta_color="off")
                sc2.metric("Est. Total Work (Heat Adjusted)", f"{sim_joules_adjusted:,.0f} J", delta=f"{sim_temp}°C Heat Factor applied", delta_color="inverse" if sim_temp > 25 else "normal")

        with tab2:
            st.header("Culturally Responsive Module")
            
            # The exact text that will be printed AND downloaded
            lesson_content = f"""MODULE: The Mechanics of the Marathon
LOCATION: Doha, Qatar
ENVIRONMENT: {sim_temp}°C Ambient Temperature

CONTEXT: 
A runner with a mass of {sim_mass} kg recently completed a {distance:.2f} km race. We are analyzing their mechanical efficiency under specific local environmental conditions.

THE DATA:
- Average Speed: {avg_speed_ms:.2f} m/s
- Average Cadence: {cadence:.0f} steps/min
- Average Stride Length: {stride_m:.2f} meters
- Baseline Energy Burned: {calories:.0f} kcal

STUDENT TASKS:
1. Kinematic Verification: Prove mathematically that a cadence of {cadence:.0f} steps/min and a stride length of {stride_m:.2f}m results in the recorded average speed of {avg_speed_ms:.2f} m/s. Show your unit conversions.

2. Kinetic Energy Profile: Calculate the runner's kinetic energy using the provided mass of {sim_mass} kg. If the runner was carrying a 3kg hydration pack, how would this alter the kinetic energy output?

3. Thermodynamics & Environment: The ambient temperature during this run was {sim_temp}°C. Explain how this heat impacts the body's mechanical efficiency (hint: consider sweat evaporation and cardiac drift). Based on the 'Est. Total Work' calculation, propose a hydration strategy for this specific climate.
"""
            
            st.markdown(lesson_content.replace('\n', '\n\n')) # Formatting for Streamlit display
            
            st.divider()
            st.download_button(
                label="📥 Download Lesson Plan for Classroom (TXT)",
                data=lesson_content,
                file_name="Marathon_Physics_Module.txt",
                mime="text/plain",
                type="primary"
            )

        with tab3:
            st.subheader("Raw Workout Metrics")
            st.dataframe(df, use_container_width=True)

    else:
        st.error("The uploaded file does not match the expected 'Metric, Value, Unit' summary format.")

else:
    st.title("Welcome to the Biometric Engine")
    st.markdown("Upload a CSV or TXT file in the sidebar to power up the engine.")
    st.image("https://images.unsplash.com/photo-1530143311094-34d807799e8f?auto=format&fit=crop&q=80&w=1200", use_container_width=True)
