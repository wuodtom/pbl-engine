import streamlit as st
import pandas as pd
import io
import google.generativeai as genai
from fpdf import FPDF

# ==========================================
# 1. SETUP & BRANDING
# ==========================================
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

# Securely configure the Gemini API from Streamlit Secrets
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except:
    st.warning("⚠️ Gemini API Key not found in Streamlit Secrets. AI generation will fail.")

# ==========================================
# 2. HELPER FUNCTIONS 
# ==========================================
def parse_workout_data(raw_csv):
    try:
        df = pd.read_csv(io.StringIO(raw_csv), sep=',', on_bad_lines='skip')
        df.columns = df.columns.str.strip()
        
        if 'Metric' not in df.columns or 'Value' not in df.columns:
            return None, None

        def get_val(metric_name):
            try:
                val = str(df.loc[df['Metric'] == metric_name, 'Value'].values[0])
                val_clean = ''.join(c for c in val if c.isdigit() or c == '.')
                return float(val_clean) if val_clean else 0.0
            except: return 0.0

        metrics = {
            'distance_km': get_val('Distance'),
            'calories': get_val('Total Calories'),
            'avg_speed_kmh': get_val('Average Speed'),
            'cadence': get_val('Average Cadence'),
            'stride_cm': get_val('Average Stride Length')
        }
        return df, metrics
    except Exception:
        return None, None

def create_lesson_pdf(text_content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    # Basic sanitization to prevent FPDF from crashing on AI-generated special characters
    clean_text = text_content.replace('**', '').replace('*', '-') 
    for line in clean_text.split('\n'):
        clean_line = line.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 8, txt=clean_line)
    return pdf.output(dest="S").encode('latin-1')

def generate_ai_lesson(metrics, sim_mass, pred_temp):
    dist = metrics['distance_km']
    spd_ms = metrics['avg_speed_kmh'] / 3.6
    
    # Switched to 'gemini-pro' for universal compatibility
    model = genai.GenerativeModel('gemini-pro')
    
    # The engineered prompt forcing the Code.org CT format
    prompt = f"""
    Act as an expert STEM educator. Create a Computational Thinking lesson plan based on this specific athletic data:
    - Distance: {dist:.2f} km
    - Calories Burned: {metrics['calories']} kcal
    - Average Speed: {spd_ms:.2f} m/s
    - Cadence: {metrics['cadence']} steps/min
    - Stride Length: {metrics['stride_cm']} cm
    - Simulated Runner Mass: {sim_mass} kg
    - Predicted Race Temperature: {pred_temp}°C

    Structure the response EXACTLY in this 4-step format, suitable for a middle/high school physics or biology class. 
    
    STEP 1: PICK A CONCEPT & PRACTICE
    STEP 2: DECOMPOSE
    STEP 3: CREATE A CONTEXT
    STEP 4: COME UP WITH AN EXERCISE
    
    Requirements for Step 4: Include a realistic scenario (e.g., running in Doha) and create 2 specific mathematical or scientific questions that force the students to use the exact data numbers provided above. 
    Do not use emojis. Keep formatting simple.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating AI lesson: {e}\n\nPlease check your API Key configuration."

# ==========================================
# 3. SIDEBAR & FILE UPLOAD
# ==========================================
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

# ==========================================
# 4. MAIN DASHBOARD UI
# ==========================================
if uploaded_file is None:
    st.title("Welcome to the Biometric Engine")
    st.markdown("Upload a CSV or TXT file in the sidebar to power up the engine.")
    st.image("https://images.unsplash.com/photo-1530143311094-34d807799e8f?auto=format&fit=crop&q=80&w=1200", use_container_width=True)
else:
    raw_csv_data = uploaded_file.getvalue().decode("utf-8")
    df, m = parse_workout_data(raw_csv_data)

    if df is None or m is None:
        st.error("The uploaded file does not match the expected 'Metric, Value, Unit' summary format.")
    else:
        spd_ms = m['avg_speed_kmh'] / 3.6
        total_joules = m['calories'] * 4184 
        total_time_sec = (m['distance_km'] * 1000) / spd_ms if spd_ms > 0 else 0

        st.title("🏃‍♂️ Biometric Performance & Prediction Engine")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Distance", f"{m['distance_km']:.2f} km")
        col2.metric("Average Speed", f"{spd_ms:.2f} m/s")
        col3.metric("Energy Expended", f"{m['calories']:.0f} kcal")
        st.divider()

        tab1, tab2, tab3, tab4 = st.tabs(["🎛️ Simulator", "⏱️ Predictor", "🤖 AI Lesson Generator", "📊 Raw Data"])

        # -- TAB 1: SIMULATOR --
        with tab1:
            st.header("Kinematics & Thermodynamics Sandbox")
            c1, c2 = st.columns([1, 2])
            with c1:
                sim_mass = st.slider("Runner Mass (kg)", 40, 120, 75)
                sim_temp = st.slider("Ambient Temp (°C)", 10, 45, 25)
            with c2:
                sim_ke = 0.5 * sim_mass * (spd_ms ** 2)
                temp_penalty = 1.0 if sim_temp <= 15 else 1.0 + ((sim_temp - 15) * 0.02)
                adj_joules = total_joules * temp_penalty * (sim_mass / 75.0) 
                
                sc1, sc2 = st.columns(2)
                sc1.metric("Live Kinetic Energy", f"{sim_ke:.0f} Joules")
                sc2.metric("Est. Total Work", f"{adj_joules:,.0f} J", f"{sim_temp}°C Heat Factor applied")

        # -- TAB 2: PREDICTOR --
        with tab2:
            st.header("Algorithmic Race Predictor")
            c1, c2 = st.columns([1, 1.5])
            with c1:
                race_type = st.selectbox("Target Race:", ["5K", "10K", "Half Marathon", "Full Marathon", "Custom"])
                if race_type == "Custom":
                    target_km = st.number_input("Custom (km)", 1.0, 100.0, 15.0)
                else:
                    target_km = {"5K":5.0, "10K":10.0, "Half Marathon":21.1, "Full Marathon":42.2}[race_type]
                pred_temp = st.slider("Race Day Temp (°C)", 10, 45, 25, key="pt")
            with c2:
                if m['distance_km'] > 0 and total_time_sec > 0:
                    pred_sec = total_time_sec * ((target_km / m['distance_km']) ** 1.06)
                    final_sec = pred_sec * (1.0 if pred_temp <= 15 else 1.0 + ((pred_temp - 15) * 0.01))
                    h, mins = int(final_sec // 3600), int((final_sec % 3600) // 60)
                    st.info(f"### Predicted Time: **{h} hrs {mins} mins**")

        # -- TAB 3: AI LESSON PLAN --
        with tab3:
            st.header("AI-Powered CT Lesson Generator")
            st.markdown("Click the button below to have the AI analyze the simulator data and generate a unique Computational Thinking lesson plan.")
            
            if st.button("✨ Generate AI Lesson Plan", type="primary"):
                with st.spinner("Analyzing biometrics and generating curriculum..."):
                    
                    # Call the AI function
                    ai_lesson_text = generate_ai_lesson(m, sim_mass, pred_temp)
                    
                    # Store it in session state so it doesn't disappear if the user clicks a slider
                    st.session_state['current_lesson'] = ai_lesson_text
            
            # Display the lesson if it exists
            if 'current_lesson' in st.session_state:
                st.success("Lesson Generated!")
                st.text(st.session_state['current_lesson'])
                st.download_button(
                    label="📄 Download AI Lesson Plan (PDF)", 
                    data=create_lesson_pdf(st.session_state['current_lesson']),  # Typo fixed here!
                    file_name="AI_CT_Lesson.pdf", 
                    mime="application/pdf"
                )

        # -- TAB 4: DATA --
        with tab4:
            st.dataframe(df, use_container_width=True)
