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
        
        # Helper function to safely pull values
        def get_val(metric_name):
            try:
                # Get the string value and clean it
                val = str(df.loc[df['Metric'] == metric_name, 'Value'].values[0])
                # Remove any letters (like 'km/h' if it got stuck in the value column)
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

        # Physics Conversions
        avg_speed_ms = avg_speed_kmh / 3.6
        stride_m = stride_cm / 100
        total_joules = calories * 4184 # 1 kcal = 4184 Joules

        # --- 3. DASHBOARD UI ---
        st.title("🏃‍♂️ Biometric Performance Analysis")
        st.markdown("Transforming summary endurance data into mathematical modeling sandboxes.")

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Distance", f"{distance:.2f} km")
        col2.metric("Average Speed", f"{avg_speed_ms:.2f} m/s")
        col3.metric("Total Energy Expended", f"{calories:.0f} kcal")

        st.divider()

        tab1, tab2 = st.tabs(["📊 Data Overview", "📝 PBL Lesson Generator"])

        with tab1:
            st.subheader("Raw Workout Metrics")
            st.dataframe(df, use_container_width=True)

        with tab2:
            st.header("Culturally Responsive Module")
            if st.button("🚀 Generate Physics Lesson", type="primary"):
                st.success("Module Generated Successfully!")
                st.markdown(f"""
                ### **Module Title: The Mechanics of the Marathon**

                **Context:** A runner at the Ooredoo marathon in Doha recently completed a {distance:.2f} km race. Instead of looking at split times, we are analyzing their overall mechanical efficiency.

                **The Data:**
                * **Average Speed:** {avg_speed_ms:.2f} m/s
                * **Average Cadence:** {cadence:.0f} steps/min
                * **Average Stride Length:** {stride_m:.2f} meters
                * **Total Energy Burned:** {calories:.0f} kcal ({total_joules:,.0f} Joules)

                **Student Task (Kinematics & Thermodynamics):**
                1. **Kinematic Verification:** Prove mathematically that a cadence of {cadence:.0f} steps/min and a stride length of {stride_m:.2f}m results in the recorded average speed of {avg_speed_ms:.2f} m/s. Show your unit conversions.
                2. **Power Output:** If the runner finished the marathon in exactly 4 hours, 17 minutes, and 42 seconds, calculate their average mechanical power output in Watts over the course of the race.
                3. **Biological Efficiency:** Human muscles are only about 20-25% efficient at converting chemical energy (food) into actual forward mechanical work. Based on the total Joules burned, calculate the actual mechanical work done to move the runner's body forward.
                """)
    else:
        st.error("The uploaded file does not match the expected 'Metric, Value, Unit' summary format.")

else:
    st.title("Welcome to the Biometric Engine")
    st.markdown("Upload a CSV or TXT file in the sidebar to power up the engine.")
    st.image("https://images.unsplash.com/photo-1530143311094-34d807799e8f?auto=format&fit=crop&q=80&w=1200", use_container_width=True)
