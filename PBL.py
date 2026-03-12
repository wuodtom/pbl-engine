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

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.warning("⚠️ Gemini API Key not found in Streamlit Secrets. AI generation will be disabled.")

# ==========================================
# 2. CORE ENGINE FUNCTIONS 
# ==========================================
def parse_workout_file(raw_csv):
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
            except Exception: 
                return 0.0

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

def create_pdf(text_content, title="Document"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, title, ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=11)
    
    # Aggressively clean text for PDF compatibility
    clean_text = text_content.replace('**', '').replace('##', '')
    clean_text = clean_text.replace('$', '').replace('\\frac', '/').replace('\\times', 'x').replace('\\', '')
    
    for line in clean_text.split('\n'):
        if line.strip().startswith('* '):
            line = line.replace('* ', '- ', 1)
        # Encode to latin-1, replacing unsupported characters
        clean_line = line.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 6, txt=clean_line)
        pdf.ln(2)
        
    return pdf.output(dest="S").encode('latin-1')

def generate_ai_curriculum(metrics, sim_mass, pred_temp, is_cohort, runner_count):
    dist = metrics['distance_km']
    spd_ms = metrics['avg_speed_kmh'] / 3.6
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    engineering_challenge = ""
    if pred_temp >= 30:
        engineering_challenge = f"""
      Task 3 (Ethno-STEM Design - 20 mins): The ambient temperature is a dangerous {pred_temp}°C. Using local materials or biomimicry inspired by desert ecosystems, engineer and draw a passive cooling garment or hydration delivery system to keep the runner's core temperature stable. Justify your design using thermodynamic principles.
        """
        
    data_context = "a single runner's data"
    if is_cohort:
         data_context = f"the statistically averaged data of a cohort of {runner_count} runners"

    prompt = f"""
    Act as an expert STEM educator. Read the following athletic data representing {data_context}:
    - Distance: {dist:.2f} km
    - Calories Burned: {metrics['calories']} kcal
    - Average Speed: {spd_ms:.2f} m/s
    - Cadence: {metrics['cadence']} steps/min
    - Stride Length: {metrics['stride_cm']} cm
    - Simulated Mass: {sim_mass} kg
    - Predicted Race Temperature: {pred_temp}°C

    CRITICAL INSTRUCTION: You must be extremely detailed. Do not give short one-sentence answers. Expand on the pedagogical theory in Step 2, and provide a fully fleshed-out narrative in Step 4. DO NOT use LaTeX formatting or math symbols like \\frac. Use plain text math only (e.g., Output / Input).

    You must output a dual-document response. 
    First, the Student Lesson Plan. 
    Then, type "===TEACHER KEY===" on its own line. 
    Finally, output the Teacher Answer Key.

    STUDENT LESSON FORMAT:
    COMPUTATIONAL THINKING LESSON PLAN

    STEP 1: PICK A CONCEPT & PRACTICE
    - Concept: [Select a specific CT concept like Pattern Recognition or Algorithmic Design]
    - Practice: [Select a practice like Tinkering or Debugging]

    STEP 2: DECOMPOSE (How to teach the concept on a theoretical level)
    - Identify Biological/Physical Stages: [Write a detailed 2-sentence breakdown of the physical variables at play]
    - Understand Logic/Algorithms: [Write a detailed 2-sentence explanation of how environmental inputs act as conditions for the mathematical model]
    - Recognize Universal Patterns: [Write a detailed 2-sentence explanation connecting this specific run to broader physics principles]

    STEP 3: CREATE A CONTEXT
    - School Subject: Science/STEM
    - Everyday Life Example: [Write a highly detailed, relatable paragraph about how students interact with this physics in their real life]
    - Essential Question: [Write a deep, multi-layered question to guide the lesson]

    STEP 4: COME UP WITH AN EXERCISE
    Exercise Title: [Creative Title]
    - Introduction (5 mins): [Provide a detailed script/activity for the teacher to introduce the hidden metrics]
    - Simulation (15 mins): Students input the dataset ({dist:.2f} km at {spd_ms:.2f} m/s) into the PBL Engine. [Explain exactly what variables they should observe changing on the dashboard].
    - Modification (20 mins): Students must tinker with the Interactive Predictor and Simulator logic. 
      Task 1: [Write a highly specific math/physics question using exactly {dist:.2f} km and {metrics['calories']} kcal. Plain text math only].
      Task 2: [Write a highly specific thermodynamic question using exactly {spd_ms:.2f} m/s and {pred_temp}°C. Plain text math only].{engineering_challenge}
    - Reflection (5 mins): [Provide detailed discussion prompts about the logical pattern: Input + Condition = Output]
    
    TEACHER KEY FORMAT:
    Provide the step-by-step mathematical solutions to the tasks from Step 4. 
    Provide a detailed 4-point grading rubric assessing Data Analysis, Algorithmic Thinking, and Modeling.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating AI lesson: {e}"

def generate_arduino_bridge(spd_ms, cadence, sim_temp):
    return f"""// STEM & Fitness: PBL Biometric Physical Computing Bridge
// Connect a standard DC Motor or LED to Pin 9 (PWM)
// This translates the runner's speed into physical output.

const int outputPin = 9; 
float runnerSpeed_ms = {spd_ms:.2f}; 
int ambientTemp = {sim_temp};

void setup() {{
  Serial.begin(9600);
  pinMode(outputPin, OUTPUT);
  Serial.println("Biometric Engine Initialized...");
}}

void loop() {{
  float heatMultiplier = 1.0;
  if (ambientTemp > 25) {{
      heatMultiplier = 1.0 + ((ambientTemp - 25) * 0.05); 
  }}
  
  // Map speed to 8-bit PWM (0-255)
  int pwmValue = map(runnerSpeed_ms * 100 * heatMultiplier, 0, 600, 0, 255);
  
  if (pwmValue > 255) pwmValue = 255; 
  if (pwmValue < 0) pwmValue = 0;

  analogWrite(outputPin, pwmValue);
  
  Serial.print("Simulating Speed: ");
  Serial.print(runnerSpeed_ms);
  Serial.print(" m/s | Temp Load: ");
  Serial.print(ambientTemp);
  Serial.print("C | Output PWM: ");
  Serial.println(pwmValue);
  
  delay(1000);
}}
"""

# ==========================================
# 3. SIDEBAR: DATA SOURCE TOGGLE
# ==========================================
with st.sidebar:
    try:
        st.image("logo-black-web.png", use_container_width=True)
    except Exception:
        st.title("STEM & Fitness")
    st.divider()
    
    data_source = st.radio("Select Data Source:", ["📁 Upload File(s)", "✍️ Manual Data Entry"])
    st.divider()
    
    uploaded_files = None
    man_dist = man_time = man_cal = man_cadence = man_stride = 0
    
    if data_source == "📁 Upload File(s)":
        st.header("Upload Center")
        uploaded_files = st.file_uploader("Drop Workout Summary CSV(s)", type=["csv", "txt"], accept_multiple_files=True)
    else:
        st.header("Manual Entry")
        st.caption("Don't have a smartwatch? Enter your run data manually below.")
        man_dist = st.number_input("Distance (km)", min_value=0.1, value=5.0, step=0.1)
        man_time = st.number_input("Total Time (minutes)", min_value=1.0, value=30.0, step=1.0)
        man_cal = st.number_input("Est. Calories Burned", min_value=10, value=350, step=10)
        man_cadence = st.number_input("Est. Cadence (steps/min)", min_value=50, value=150, step=5)
        man_stride = st.number_input("Est. Stride Length (cm)", min_value=30, value=90, step=5)
        
    st.divider()
    st.markdown("Developed by **Mr. Dickens** | *stemandfitness.com*")

# ==========================================
# 4. MAIN DASHBOARD UI & LOGIC
# ==========================================
has_data = False
parsed_metrics = []
raw_dfs = []

if data_source == "📁 Upload File(s)" and uploaded_files:
    for file in uploaded_files:
        raw_data = file.getvalue().decode("utf-8")
        df, m = parse_workout_file(raw_data)
        if m is not None:
            parsed_metrics.append(m)
            raw_dfs.append(df)
    if parsed_metrics:
        has_data = True
elif data_source == "✍️ Manual Data Entry":
    # Failsafe: Prevent division by zero if user clears the box
    safe_time = man_time if man_time > 0 else 1.0 
    man_speed_ms = (man_dist * 1000) / (safe_time * 60)
    man_speed_kmh = man_speed_ms * 3.6
    
    manual_m = {
        'distance_km': man_dist,
        'calories': man_cal,
        'avg_speed_kmh': man_speed_kmh,
        'cadence': man_cadence,
        'stride_cm': man_stride
    }
    parsed_metrics.append(manual_m)
    raw_dfs.append(pd.DataFrame([manual_m]))
    has_data = True

if not has_data:
    st.title("Welcome to the Biometric Engine")
    st.markdown("Upload workout files or manually enter data in the sidebar to power up the engine.")
    st.image("https://images.unsplash.com/photo-1530143311094-34d807799e8f?auto=format&fit=crop&q=80&w=1200", use_container_width=True)
else:
    runner_count = len(parsed_metrics)
    is_cohort = runner_count > 1
    
    avg_m = {
        'distance_km': sum(x['distance_km'] for x in parsed_metrics) / runner_count,
        'calories': sum(x['calories'] for x in parsed_metrics) / runner_count,
        'avg_speed_kmh': sum(x['avg_speed_kmh'] for x in parsed_metrics) / runner_count,
        'cadence': sum(x['cadence'] for x in parsed_metrics) / runner_count,
        'stride_cm': sum(x['stride_cm'] for x in parsed_metrics) / runner_count,
    }

    spd_ms = avg_m['avg_speed_kmh'] / 3.6
    total_joules = avg_m['calories'] * 4184 
    total_time_sec = (avg_m['distance_km'] * 1000) / spd_ms if spd_ms > 0 else 0

    st.title("🏃‍♂️ Biometric Performance & Prediction Engine")
    if is_cohort:
        st.success(f"📊 Cohort Mode Active: Averaging data from {runner_count} athletes.")
    elif data_source == "✍️ Manual Data Entry":
        st.info("✍️ Manual Entry Mode Active: Computing physics from user input.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Mean Distance", f"{avg_m['distance_km']:.2f} km")
    col2.metric("Mean Speed", f"{spd_ms:.2f} m/s")
    col3.metric("Mean Energy Expended", f"{avg_m['calories']:.0f} kcal")
    st.divider()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🎛️ Simulator", "⏱️ Predictor", "🤖 Curriculum Suite", "🔌 Arduino Bridge", "📊 Raw Data"])

    # -- TAB 1: SIMULATOR --
    with tab1:
        st.header("Kinematics & Thermodynamics Sandbox")
        c1, c2 = st.columns([1, 2])
        with c1:
            sim_mass = st.slider("Runner Mass (kg)", 40, 120, 75)
            sim_temp = st.slider("Ambient Temp (°C)", 10, 50, 25)
        with c2:
            sim_ke = 0.5 * sim_mass * (spd_ms ** 2)
            temp_penalty = 1.0 if sim_temp <= 15 else 1.0 + ((sim_temp - 15) * 0.02)
            adj_joules = total_joules * temp_penalty * (sim_mass / 75.0) 
            
            sc1, sc2 = st.columns(2)
            sc1.metric("Live Kinetic Energy", f"{sim_ke:.0f} Joules")
            sc2.metric("Est. Total Work", f"{adj_joules:,.0f} J", f"{sim_temp}°C Heat Factor applied")
            
            if sim_temp >= 30:
                st.warning("🔥 Extreme Heat Detected: The Ethno-STEM Design Challenge will automatically unlock in the Curriculum generator.")

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
            pred_temp = st.slider("Race Day Temp (°C)", 10, 50, 25, key="pt")
        with c2:
            if avg_m['distance_km'] > 0 and total_time_sec > 0:
                pred_sec = total_time_sec * ((target_km / avg_m['distance_km']) ** 1.06)
                final_sec = pred_sec * (1.0 if pred_temp <= 15 else 1.0 + ((pred_temp - 15) * 0.01))
                h, mins = int(final_sec // 3600), int((final_sec % 3600) // 60)
                st.info(f"### Predicted Time: **{h} hrs {mins} mins**")

    # -- TAB 3: CURRICULUM SUITE --
    with tab3:
        st.header("AI-Powered Educator Suite")
        st.markdown("Generates a student handout and a private teacher grading rubric based on the current simulator states.")
        
        if st.button("✨ Generate Full Curriculum", type="primary"):
            with st.spinner("Decomposing theory and generating curriculum..."):
                full_text = generate_ai_curriculum(avg_m, sim_mass, pred_temp, is_cohort, runner_count)
                
                safe_text = full_text.replace("**===TEACHER KEY===**", "===TEACHER KEY===")
                
                if "===TEACHER KEY===" in safe_text:
                    parts = safe_text.split("===TEACHER KEY===")
                    st.session_state['student_lesson'] = parts[0].strip()
                    st.session_state['teacher_rubric'] = parts[1].strip()
                else:
                    st.session_state['student_lesson'] = safe_text
                    st.session_state['teacher_rubric'] = "Error: AI did not separate the rubric correctly. Please try generating again."
        
        if 'student_lesson' in st.session_state:
            st.success("Curriculum Generated Successfully!")
            
            cur_tab1, cur_tab2 = st.tabs(["📄 Student Lesson Plan", "🔒 Teacher Answer Key & Rubric"])
            
            with cur_tab1:
                st.markdown(st.session_state['student_lesson'])
                st.download_button("Download Student Handout (PDF)", data=create_pdf(st.session_state['student_lesson'], title="STEM Lesson Plan"), file_name="Student_Lesson.pdf", mime="application/pdf")
                
            with cur_tab2:
                st.info("The following solutions and rubrics are based strictly on the mathematical model.")
                st.markdown(st.session_state['teacher_rubric'])
                st.download_button("Download Teacher Key (PDF)", data=create_pdf(st.session_state['teacher_rubric'], title="Teacher Answer Key & Rubric"), file_name="Teacher_Rubric.pdf", mime="application/pdf")

    # -- TAB 4: ARDUINO BRIDGE --
    with tab4:
        st.header("Physical Computing Bridge (Arduino)")
        st.markdown("Export the current kinematic and thermodynamic data to a microcontroller to build physical models.")
        arduino_code = generate_arduino_bridge(spd_ms, avg_m['cadence'], sim_temp)
        st.code(arduino_code, language="cpp")
        st.download_button("Download .ino File", data=arduino_code, file_name="PBL_Biometric.ino", mime="text/plain")

    # -- TAB 5: RAW DATA --
    with tab5:
        if is_cohort:
            st.subheader(f"Cohort Data Preview ({runner_count} Runners)")
            comp_data = []
            for i, m in enumerate(parsed_metrics):
                comp_data.append({"Runner": f"Runner {i+1}", "Distance (km)": m['distance_km'], "Speed (km/h)": m['avg_speed_kmh'], "Calories": m['calories']})
            st.dataframe(pd.DataFrame(comp_data), use_container_width=True)
        else:
            st.subheader("Raw Data Model")
            st.dataframe(raw_dfs[0], use_container_width=True)
            if data_source == "✍️ Manual Data Entry":
                st.caption("This data frame was generated dynamically from your manual inputs.")
