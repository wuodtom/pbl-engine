import streamlit as st
import pandas as pd
import io
from fpdf import FPDF

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

    # READ THE SUMMARY DATA
    try:
        df = pd.read_csv(io.StringIO(raw_csv_data), sep=',', on_bad_lines='skip')
        df.columns = df.columns.str.strip()
    except Exception as e:
        st.error(f"Could not read file. Error: {e}")
        st.stop()

    if 'Metric' in df.columns and 'Value' in df.columns:
        
        def get_val(metric_name):
            try:
                val = str(df.loc[df['Metric'] == metric_name, 'Value'].values[0])
                val_clean = ''.join(c for c in val if c.isdigit() or c == '.')
                return float(val_clean) if val_clean else 0.0
            except:
                return 0.0

        # Extract Core Metrics
        distance_km = get_val('Distance')
        calories = get_val('Total Calories')
        avg_speed_kmh = get_val('Average Speed')
        cadence = get_val('Average Cadence')
        stride_cm = get_val('Average Stride Length')

        # Conversions
        avg_speed_ms = avg_speed_kmh / 3.6
        stride_m = stride_cm / 100
        total_joules = calories * 4184 
        total_time_seconds = (distance_km * 1000) / avg_speed_ms if avg_speed_ms > 0 else 0

        # --- DASHBOARD UI ---
        st.title("🏃‍♂️ Biometric Performance & Prediction Engine")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Distance", f"{distance_km:.2f} km")
        col2.metric("Average Speed", f"{avg_speed_ms:.2f} m/s")
        col3.metric("Energy Expended", f"{calories:.0f} kcal")

        st.divider()

        # The Four Core Tabs
        tab1, tab2, tab3, tab4 = st.tabs(["🎛️ Kinematics Simulator", "⏱️ Race Predictor", "📝 CT Lesson (PDF)", "📊 Raw Data"])

        # TAB 1: THE SIMULATOR
        with tab1:
            st.header("Kinematics & Thermodynamics Sandbox")
            st.markdown("Adjust the variables below to see how physical and environmental factors alter the mathematical model.")
            
            c1, c2 = st.columns([1, 2])
            with c1:
                st.subheader("Set Variables")
                sim_mass = st.slider("Runner Mass (kg)", min_value=40, max_value=120, value=75, step=1)
                sim_temp = st.slider("Ambient Temperature (°C)", min_value=10, max_value=45, value=25, step=1)
            
            with c2:
                st.subheader("Live Physics Output")
                sim_ke = 0.5 * sim_mass * (avg_speed_ms ** 2)
                temp_penalty = 1.0 if sim_temp <= 15 else 1.0 + ((sim_temp - 15) * 0.02)
                sim_joules_adjusted = total_joules * temp_penalty * (sim_mass / 75.0) 
                
                sc1, sc2 = st.columns(2)
                sc1.metric("Live Kinetic Energy", f"{sim_ke:.0f} Joules", delta="Calculated from Mass & Speed", delta_color="off")
                sc2.metric("Est. Total Work (Heat Adjusted)", f"{sim_joules_adjusted:,.0f} J", delta=f"{sim_temp}°C Heat Factor applied", delta_color="inverse" if sim_temp > 25 else "normal")

        # TAB 2: THE PREDICTOR
        with tab2:
            st.header("Algorithmic Race Predictor")
            st.markdown("Predict finish times for different race distances using Peter Riegel's formula.")
            
            c1, c2 = st.columns([1, 1.5])
            with c1:
                target_options = {"5K": 5.0, "10K": 10.0, "Half Marathon": 21.1, "Full Marathon": 42.2, "Custom": 1.0}
                race_type = st.selectbox("Target Race:", list(target_options.keys()))
                
                if race_type == "Custom":
                    target_km = st.number_input("Enter Custom Distance (km)", min_value=1.0, max_value=100.0, value=15.0)
                else:
                    target_km = target_options[race_type]

                pred_temp = st.slider("Predicted Race Day Temp (°C)", 10, 45, 25, key="pred_temp")

            with c2:
                if distance_km > 0 and total_time_seconds > 0:
                    predicted_seconds = total_time_seconds * ((target_km / distance_km) ** 1.06)
                    temp_penalty_pred = 1.0 if pred_temp <= 15 else 1.0 + ((pred_temp - 15) * 0.01)
                    final_seconds = predicted_seconds * temp_penalty_pred
                    
                    h = int(final_seconds // 3600)
                    m = int((final_seconds % 3600) // 60)
                    
                    st.info(f"### Predicted Finish Time: **{h} hrs {m} mins**")
                    st.write(f"**Target Distance:** {target_km} km")
                    st.write(f"**Calculated using:** Riegel's Formula factored with a {pred_temp}°C thermodynamic load.")
                else:
                    st.error("Distance and Speed must be greater than zero to predict.")

        # TAB 3: THE PBL LESSON & PDF
        with tab3:
            st.header("Computational Thinking Lesson Plan")
            
            lesson_text = f"""Lesson Plan: Predictive Algorithmic Modeling
Subject: Science/STEM
Tool: PBL Engine (stemandfitness.com)
Duration: 45 minutes

COMPUTATIONAL THINKING LESSON PLAN

STEP 1: PICK A CONCEPT & PRACTICE
Concept: Mathematical Modeling & Algorithms
Practice: Tinkering & Data Analysis

STEP 2: DECOMPOSE
- Identify Biometrics: Break down the variables (speed, distance, time) from a real dataset.
- Understand the Algorithm: Explain how Riegel's Formula acts as a logical condition to scale endurance.
- Recognize Universal Patterns: Teach students that environmental inputs act as modifiers to algorithmic outputs.

STEP 3: CREATE A CONTEXT
School Subject: Science/STEM
Everyday Life Example: How smartwatches and fitness apps predict finish times based on smaller everyday training runs.
Essential Question: How can we use mathematical algorithms to predict human physical performance, and what are the limitations of these models?

STEP 4: COME UP WITH AN EXERCISE
Exercise Title: The Biometric Predictor Modification

Introduction (5 mins): Discuss how fitness trackers predict race times. Introduce Riegel's formula.

Simulation (15 mins): Students upload the {distance_km:.1f}km dataset into the PBL Engine. They observe the baseline metrics and calculate the runner's baseline speed.

Modification (20 mins): Students must "tinker" with the Interactive Predictor and Simulator. Task: "Determine the predicted finish time and energy load if the temperature in Doha rises." They observe how the temperature variable modifies the final algorithm.

Reflection (5 mins): Discuss the limitations of the model. Does the algorithm account for hills, wind, or dehydration? Why or why not?
"""
            st.text(lesson_text)
            
            def create_pdf(text_content):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=11)
                for line in text_content.split('\n'):
                    clean_line = line.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0, 8, txt=clean_line)
                return pdf.output(dest="S").encode('latin-1')

            st.download_button(
                label="📄 Download CT Lesson Plan (PDF)",
                data=create_pdf(lesson_text),
                file_name="CT_Lesson_Plan.pdf",
                mime="application/pdf",
                type="primary"
            )

        # TAB 4: RAW DATA
        with tab4:
            st.subheader("Raw Workout Metrics")
            st.dataframe(df, use_container_width=True)

    else:
        st.error("The uploaded file does not match the expected 'Metric, Value, Unit' summary format.")

else:
    # HERO IMAGE & EMPTY STATE
    st.title("Welcome to the Biometric Engine")
    st.markdown("Upload a CSV or TXT file in the sidebar to power up the engine.")
    st.image("https://images.unsplash.com/photo-1530143311094-34d807799e8f?auto=format&fit=crop&q=80&w=1200", use_container_width=True)
