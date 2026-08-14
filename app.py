import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import plotly.graph_objects as go
from preprocess import clean_resume_text, extract_text_from_pdf
from skill_analysis import extract_skills
from scoring import calculate_benchmark_metrics, generate_suggestions

# --- PAGE CONFIG ---
st.set_page_config(page_title="ResumeBench | AI Dashboard", page_icon="🚀", layout="wide")

# --- FUTURISTIC NEON CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        background: radial-gradient(circle at top right, #1e1b4b, #0f172a 50%, #020617 100%);
        color: #e2e8f0;
        font-family: 'Outfit', sans-serif;
    }

    /* Glassmorphism Card Premium */
    .glass-card {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 40px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
        margin-bottom: 30px;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border: 1px solid rgba(59, 130, 246, 0.3);
        transform: translateY(-5px);
    }

    .neon-text {
        font-family: 'Space Grotesk', sans-serif;
        background: linear-gradient(90deg, #3b82f6, #a855f7, #3b82f6);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite;
        font-weight: 800;
    }

    @keyframes shine {
        to { background-position: 200% center; }
    }

    /* Skill Matrix Styling */
    .skill-matrix-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
        gap: 15px;
        margin-top: 20px;
    }

    .skill-box {
        padding: 15px;
        border-radius: 16px;
        text-align: center;
        font-weight: 600;
        font-size: 0.9rem;
        border: 1px solid transparent;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .skill-box.match {
        background: rgba(34, 211, 238, 0.05);
        color: #22d3ee;
        border-color: rgba(34, 211, 238, 0.2);
        box-shadow: 0 0 15px rgba(34, 211, 238, 0.1);
    }
    .skill-box.match:hover {
        background: rgba(34, 211, 238, 0.15);
        box-shadow: 0 0 25px rgba(34, 211, 238, 0.3);
    }

    .skill-box.missing {
        background: rgba(248, 113, 113, 0.05);
        color: #f87171;
        border-color: rgba(248, 113, 113, 0.2);
    }
    .skill-box.missing:hover {
        background: rgba(248, 113, 113, 0.1);
        box-shadow: 0 0 20px rgba(248, 113, 113, 0.2);
    }

    .stat-label { color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; font-size: 0.75rem; font-weight: 700; }
    .stat-value { font-size: 2.2rem; font-weight: 800; color: white; margin-bottom: 5px; }

    h1, h2, h3 { color: #ffffff !important; }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #3b82f6 0%, #a855f7 100%);
        height: 12px;
        border-radius: 10px;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- LOAD ENGINE ---
@st.cache_resource
def load_engine():
    try:
        with open('models/classifier.pkl', 'rb') as f: model = pickle.load(f)
        with open('models/tfidf.pkl', 'rb') as f: tfidf = pickle.load(f)
        with open('models/label_encoder.pkl', 'rb') as f: le = pickle.load(f)
        with open('models/role_skills.pkl', 'rb') as f: role_skills = pickle.load(f)
        
        # Load Pre-Cleaned Dataset for performance
        data_path = 'dataset/resume_data_cleaned.csv'
        if not os.path.exists(data_path):
            data_path = 'dataset/resume_data.csv'
            
        data = pd.read_csv(data_path)
        return model, tfidf, le, role_skills, data
    except: return None, None, None, None, None

model, tfidf, le, role_skills, df_dataset = load_engine()

# --- APP LAYOUT ---
st.markdown("<h1 class='neon-text' style='text-align:center; font-size:3rem; margin-bottom:10px;'>ML Resume Intelligence Engine</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#94a3b8; font-size:1.1rem; margin-bottom:50px;'>Pattern-Based Classification & Benchmarking Dashboard</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Profile PDF", type=["pdf"])

if uploaded_file and model:
    with st.spinner("Analyzing profile vectors..."):
        try:
            text = extract_text_from_pdf(uploaded_file)
            cleaned = clean_resume_text(text)
            
            if not cleaned:
                st.error("Document core analysis failed. Please ensure the PDF contains readable text.")
                st.stop()

            # Prediction + Confidence
            vec = tfidf.transform([cleaned])
            probs = model.predict_proba(vec)[0]
            pred_id = model.predict(vec)[0]
            role = le.inverse_transform([pred_id])[0]
            confidence = float(probs[pred_id] * 100)
            
            # Complex Benchmarking
            res = calculate_benchmark_metrics(cleaned, role, df_dataset, tfidf, role_skills, confidence)
            readiness, skill_match, quality, keyword_val, matched, missing, role_count, benchmark_count, high_match, top_benchmarks = res

            # --- TOP ROW: ROLE & READINESS ---
            st.markdown(f"""
                <div class='glass-card'>
                    <div style='display:flex; justify-content:space-between; align-items:center; gap:20px;'>
                        <div style='flex:1;'>
                            <p class='stat-label'>Classified Industry Domain</p>
                            <h1 style='font-size:3.5rem; margin:0; line-height:1;' class='neon-text'>{role}</h1>
                        </div>
                        <div style='text-align:right; padding-left: 20px; border-left: 1px solid rgba(255,255,255,0.1);'>
                            <p class='stat-label'>Job Readiness Score</p>
                            <h1 style='font-size:3.5rem; margin:0; color:#3b82f6 !important; line-height:1;'>{readiness:.1f}%</h1>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # --- BIG SKILL MATRIX SECTION ---
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='text-align:center; margin-bottom:40px;'>Skill Analysis & Evaluation</h2>", unsafe_allow_html=True)
            
            s_col1, s_col2 = st.columns(2)
            with s_col1:
                st.markdown("<h3 style='color:#22d3ee !important; font-size:1.2rem;'>✓ Identified Assets</h3>", unsafe_allow_html=True)
                if matched:
                    st.markdown("<div class='skill-matrix-container'>", unsafe_allow_html=True)
                    for s in matched:
                        st.markdown(f"<div class='skill-box match'>{s.upper()}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                else: 
                    st.markdown("<p style='color:#475569; padding:20px;'>No direct matches detected in profile vector.</p>", unsafe_allow_html=True)

            with s_col2:
                st.markdown("<h3 style='color:#f87171 !important; font-size:1.2rem;'>✕ Critical Gaps</h3>", unsafe_allow_html=True)
                if missing:
                    st.markdown("<div class='skill-matrix-container'>", unsafe_allow_html=True)
                    for s in missing:
                        st.markdown(f"<div class='skill-box missing'>{s.upper()}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                else: 
                    st.markdown("<div style='background:rgba(16, 185, 129, 0.1); padding:20px; border-radius:15px; border:1px solid #10b981; text-align:center;'><p style='color:#10b981; margin:0;'>CORE COMPETENCIES SECURED</p></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # --- LOWER ROW: ROADMAP ---
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("<h3 style='color:#3b82f6 !important;'>Architectural Roadmap</h3>", unsafe_allow_html=True)
            st.markdown("<div style='margin-top:20px;'>", unsafe_allow_html=True)
            tips = generate_suggestions(missing, role)
            for tip in tips:
                st.markdown(f"<p style='color:#94a3b8; margin-bottom:18px; font-size:1.1rem;'>⚡ {tip}</p>", unsafe_allow_html=True)
            st.markdown("</div></div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Neural Dashboard Exception: {str(e)}")
            st.info("Ensure models are trained and PDF encoding is standard.")
else:
    # --- MINIMAL LANDING PAGE ---
    st.markdown("<div style='text-align:center; padding:100px 0;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size:4.5rem; margin-bottom:10px;' class='neon-text'>ML Career Vector Engine</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:1.4rem; color:#94a3b8; max-width:800px; margin:0 auto 40px;'>Professional Grade Resume Classification & Benchmark Intelligence</p>", unsafe_allow_html=True)
    
    st.markdown("<div style='max-width:600px; margin: 0 auto; padding:40px; background:rgba(255,255,255,0.02); border-radius:24px; border:1px dashed rgba(255,255,255,0.1); text-align:center;'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#3b82f6; font-weight:700; text-transform:uppercase;'>Ready for Analysis</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94a3b8; font-size:0.9rem; margin-bottom:20px;'>Upload your professional PDF to generate deep ML benchmarks</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div style='text-align:center; padding:40px; opacity:0.6; color:#94a3b8;'><p>⚡ System operational. ML models initialized.</p></div>", unsafe_allow_html=True)
