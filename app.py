# app.py - NutriMind Professional Dark Theme with Gemini AI
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time
from PIL import Image
import io
import random
import json
import base64
import requests
import re

# ========== CRITICAL: Initialize ALL session state at TOP ==========
if 'app_initialized' not in st.session_state:
    st.session_state.app_initialized = True
    st.session_state.user = None
    st.session_state.food_logs = []
    st.session_state.exercise_logs = []
    st.session_state.water_intake = 0
    st.session_state.daily_totals = {
        'calories': 0,
        'protein': 0,
        'carbs': 0,
        'fats': 0,
        'calories_burned': 0,
        'water': 0
    }
    st.session_state.goals = {
        'calories': 2000,
        'protein': 50,
        'carbs': 250,
        'fats': 65,
        'exercise_minutes': 30
    }
    st.session_state.diet_preference = "All"
    st.session_state.current_analyzed_food = None
    st.session_state.show_success = False
    st.session_state.success_message = ""
    st.session_state.page = "dashboard"

# Configure the page
st.set_page_config(
    page_title="NutriMind - AI Nutrition Assistant",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== PROFESSIONAL DARK MODE CSS ==========
st.markdown("""
<style>
    /* ===== PROFESSIONAL DARK THEME ===== */
    :root {
        --primary: #00B894;
        --primary-dark: #00A08A;
        --primary-light: #00FFD4;
        --secondary: #6C63FF;
        --accent: #FF6B9D;
        --bg-dark: #0F172A;
        --bg-darker: #0A1123;
        --bg-card: #1E293B;
        --bg-card-light: #2D3748;
        --text-primary: #F1F5F9;
        --text-secondary: #CBD5E1;
        --text-muted: #94A3B8;
        --border: #334155;
        --border-light: #475569;
        --success: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
        --info: #3B82F6;
        --radius: 12px;
        --shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        --shadow-lg: 0 20px 40px rgba(0, 0, 0, 0.4);
    }
    
    /* Main App Background */
    .stApp {
        background: linear-gradient(135deg, var(--bg-darker) 0%, var(--bg-dark) 100%);
        color: var(--text-primary);
    }
    
    /* Professional Header */
    .main-header {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        text-align: center;
        margin: 1.5rem 0 0.5rem !important;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 50%, var(--accent) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.5px;
        line-height: 1.1;
    }
    
    .slogan {
        text-align: center;
        font-size: 1.25rem;
        color: var(--text-secondary);
        font-weight: 400;
        letter-spacing: 1px;
        margin: 0 0 2.5rem;
        opacity: 0.9;
    }
    
    /* Professional Cards */
    .pro-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.75rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .pro-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(to bottom, var(--primary), var(--secondary));
    }
    
    .pro-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .card-icon {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        color: white;
        box-shadow: 0 4px 12px rgba(0, 184, 148, 0.3);
    }
    
    /* Stats Cards */
    .stat-card {
        background: linear-gradient(135deg, var(--bg-card), var(--bg-card-light));
        border-radius: var(--radius);
        padding: 1.5rem;
        text-align: center;
        border: 1px solid var(--border);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    }
    
    .stat-value {
        font-size: 2.25rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0.75rem 0;
    }
    
    .stat-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Progress Bars */
    .progress-container {
        background: var(--border);
        border-radius: 100px;
        height: 8px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        border-radius: 100px;
        transition: width 0.6s ease;
        position: relative;
        overflow: hidden;
    }
    
    .progress-bar::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    /* Food Log Items */
    .food-log-item-pro {
        background: var(--bg-card);
        border-radius: 10px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        border-left: 4px solid var(--primary);
        border: 1px solid var(--border);
        transition: all 0.2s ease;
    }
    
    .food-log-item-pro:hover {
        background: var(--bg-card-light);
        transform: translateX(5px);
    }
    
    /* Exercise Log Items */
    .exercise-log-item-pro {
        background: var(--bg-card);
        border-radius: 10px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        border-left: 4px solid var(--secondary);
        border: 1px solid var(--border);
        transition: all 0.2s ease;
    }
    
    .exercise-log-item-pro:hover {
        background: var(--bg-card-light);
        transform: translateX(5px);
    }
    
    /* Success Toast */
    .success-toast-pro {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white;
        padding: 1.25rem 1.5rem;
        border-radius: var(--radius);
        margin: 1.5rem 0;
        animation: slideDown 0.5s ease;
        box-shadow: 0 8px 25px rgba(0, 184, 148, 0.4);
        border: none;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    @keyframes slideDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Scan Options */
    .scan-option-pro {
        background: var(--bg-card);
        border: 2px dashed var(--border-light);
        border-radius: var(--radius);
        padding: 2rem;
        margin: 1.5rem 0;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .scan-option-pro:hover {
        border-color: var(--primary);
        background: var(--bg-card-light);
        transform: translateY(-3px);
    }
    
    /* Meal Suggestion Cards */
    .meal-suggestion-card-pro {
        background: var(--bg-card);
        border-radius: var(--radius);
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid var(--accent);
        border: 1px solid var(--border);
        transition: all 0.3s ease;
    }
    
    .meal-suggestion-card-pro:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        border-color: var(--accent);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.875rem 1.75rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(0, 184, 148, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(0, 184, 148, 0.4) !important;
    }
    
    /* Secondary Button */
    .stButton > button[kind="secondary"] {
        background: transparent !important;
        color: var(--primary) !important;
        border: 2px solid var(--primary) !important;
        box-shadow: none !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--bg-darker) 0%, var(--bg-dark) 100%);
        border-right: 1px solid var(--border);
    }
    
    /* Metrics */
    .stMetric {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 1.25rem !important;
        box-shadow: var(--shadow) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--bg-card);
        padding: 8px;
        border-radius: var(--radius);
        border: 1px solid var(--border);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 2px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(0, 184, 148, 0.1) !important;
    }
    
    /* Sliders */
    .stSlider > div > div > div {
        background: var(--border) !important;
    }
    
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, var(--primary), var(--secondary)) !important;
    }
    
    /* Radio Buttons */
    .stRadio > div {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        padding: 1rem !important;
    }
    
    /* Plotly Charts */
    .js-plotly-plot .plotly {
        background: var(--bg-card) !important;
    }
    
    /* File Uploader */
    .stFileUploader > div > div {
        background: var(--bg-card) !important;
        border: 2px dashed var(--border) !important;
        border-radius: var(--radius) !important;
    }
    
    /* Info/Warning/Success Boxes */
    .stInfo, .stWarning, .stSuccess, .stError {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius) !important;
        border-left: 4px solid !important;
    }
    
    .stInfo {
        border-left-color: var(--info) !important;
    }
    
    .stWarning {
        border-left-color: var(--warning) !important;
    }
    
    .stSuccess {
        border-left-color: var(--success) !important;
    }
    
    .stError {
        border-left-color: var(--danger) !important;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-dark);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--border-light);
    }
    
    /* Fix grid spacing */
    .grid-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .grid-item {
        text-align: center;
    }
    
    /* Fix for water intake display */
    .water-display {
        background: var(--bg-card-light);
        padding: 0.75rem;
        border-radius: 8px;
        margin-top: 1rem;
        border: 1px solid var(--border);
    }
</style>
""", unsafe_allow_html=True)

# ... [Keep all the existing functions from your original code - analyze_food_with_gemini, 
# get_fallback_nutrition, get_exercise_suggestions, calculate_calorie_target, 
# calculate_protein_target, calculate_exercise_target, get_meal_suggestions, 
# save_food_to_session, save_exercise_to_session] 
# Make sure to copy ALL your existing functions here...

# ========== PROFESSIONAL HEADER ==========
st.markdown('<h1 class="main-header">NutriMind</h1>', unsafe_allow_html=True)
st.markdown('<p class="slogan">Scan • Track • Grow</p>', unsafe_allow_html=True)

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("""
    <div class="pro-card" style="margin-bottom: 2rem;">
        <div class="card-header">
            <div class="card-icon">👤</div>
            <h3 style="margin: 0; color: var(--text-primary);">User Profile</h3>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.user is None:
        name = st.text_input("Your Name", value="")
        age = st.number_input("Age", min_value=1, max_value=100, value=21, step=1)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        activity_level = st.select_slider(
            "Activity Level",
            options=["sedentary", "light", "moderate", "active", "very active"],
            value="moderate"
        )
        
        if age and gender:
            calorie_target = calculate_calorie_target(age, gender, activity_level)
            protein_target = calculate_protein_target(age, gender, calorie_target)
            exercise_target = calculate_exercise_target(age)
            
            st.markdown("### Your Recommended Targets:")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Calories", f"{calorie_target}")
            with col2:
                st.metric("Protein", f"{protein_target}g")
            with col3:
                st.metric("Exercise", f"{exercise_target} min")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Create Profile", type="primary", use_container_width=True):
                if name:
                    calorie_target = calculate_calorie_target(age, gender, activity_level)
                    protein_target = calculate_protein_target(age, gender, calorie_target)
                    exercise_target = calculate_exercise_target(age)
                    
                    st.session_state.user = {
                        'name': name,
                        'age': age,
                        'gender': gender,
                        'activity_level': activity_level,
                        'joined': datetime.now().strftime("%Y-%m-%d")
                    }
                    
                    st.session_state.goals = {
                        'calories': calorie_target,
                        'protein': protein_target,
                        'carbs': int(calorie_target * 0.5 / 4),
                        'fats': int(calorie_target * 0.25 / 9),
                        'exercise_minutes': exercise_target
                    }
                    
                    st.success(f"Welcome {name}! 🎉")
                    st.rerun()
                else:
                    st.error("Please enter your name")
        
        with col2:
            if st.button("Demo Mode", use_container_width=True):
                st.session_state.user = {
                    'name': "Demo User",
                    'age': 25,
                    'gender': "Male",
                    'activity_level': "moderate",
                    'joined': datetime.now().strftime("%Y-%m-%d")
                }
                st.rerun()
    else:
        st.markdown(f"""
        <div class="pro-card">
            <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem;">
                <div style="width: 60px; height: 60px; background: linear-gradient(135deg, var(--primary), var(--secondary)); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 1.75rem; color: white;">
                    {st.session_state.user['name'][0].upper()}
                </div>
                <div>
                    <h4 style="margin: 0; color: var(--text-primary);">{st.session_state.user['name']}</h4>
                    <p style="margin: 0.25rem 0 0; color: var(--text-secondary); font-size: 0.875rem;">
                        Age: {st.session_state.user['age']} • {st.session_state.user['gender']}
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Logout", type="secondary", use_container_width=True):
            st.session_state.user = None
            st.session_state.food_logs = []
            st.session_state.exercise_logs = []
            st.session_state.daily_totals = {'calories': 0, 'protein': 0, 'carbs': 0, 'fats': 0, 'calories_burned': 0, 'water': 0}
            st.rerun()
    
    st.markdown("""
    <div class="pro-card">
        <div class="card-header">
            <div class="card-icon">🎯</div>
            <h3 style="margin: 0; color: var(--text-primary);">Daily Goals</h3>
        </div>
    """, unsafe_allow_html=True)
    
    calories_goal = st.slider("Calories Goal", 1000, 3000, st.session_state.goals['calories'], 100)
    protein_goal = st.slider("Protein Goal (g)", 30, 150, st.session_state.goals['protein'], 5)
    exercise_goal = st.slider("Exercise Goal (min)", 0, 120, st.session_state.goals['exercise_minutes'], 5)
    
    if st.button("Update Goals", key="update_goals", use_container_width=True):
        st.session_state.goals['calories'] = calories_goal
        st.session_state.goals['protein'] = protein_goal
        st.session_state.goals['exercise_minutes'] = exercise_goal
        st.success("Goals updated! 💪")
        time.sleep(1)
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="pro-card">
        <div class="card-header">
            <div class="card-icon">🥗</div>
            <h3 style="margin: 0; color: var(--text-primary);">Diet Preference</h3>
        </div>
    """, unsafe_allow_html=True)
    
    diet_options = ["All", "Vegetarian", "Non-Vegetarian", "Eggetarian"]
    
    for diet in diet_options:
        is_active = (st.session_state.diet_preference == diet)
        if st.button(
            diet,
            key=f"diet_{diet}",
            type="primary" if is_active else "secondary",
            use_container_width=True
        ):
            st.session_state.diet_preference = diet
            st.rerun()
    
    st.markdown(f"""
    <div class="water-display">
        <p style="margin: 0; color: var(--text-primary); font-weight: 500;">
            Selected: <span style="color: var(--primary);">{st.session_state.diet_preference}</span>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class="pro-card">
        <div class="card-header">
            <div class="card-icon">💧</div>
            <h3 style="margin: 0; color: var(--text-primary);">Water Intake</h3>
        </div>
    """, unsafe_allow_html=True)
    
    water_col1, water_col2 = st.columns(2)
    with water_col1:
        current_water = st.session_state.daily_totals.get('water', 0)
        water_percent = min(100, (current_water / 2000) * 100)
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="font-size: 1.75rem; font-weight: 700; color: var(--primary);">{current_water}ml</div>
            <div style="font-size: 0.875rem; color: var(--text-secondary);">Today's Water</div>
            <div class="progress-container" style="margin-top: 0.5rem;">
                <div class="progress-bar" style="width: {water_percent}%"></div>
            </div>
            <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">{water_percent:.0f}% of goal</div>
        </div>
        """, unsafe_allow_html=True)
    
    with water_col2:
        water_to_add = st.selectbox("Add water", [250, 500, 750, 1000], index=0, label_visibility="collapsed")
        if st.button("💧 Add Water", use_container_width=True):
            st.session_state.water_intake += water_to_add
            st.session_state.daily_totals['water'] = st.session_state.water_intake
            st.success(f"Added {water_to_add}ml water!")
            time.sleep(0.5)
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ========== MAIN APP ==========
if st.session_state.user is None:
    st.markdown("""
    <div class="pro-card">
        <div class="card-header">
            <div class="card-icon">🚀</div>
            <h2 style="margin: 0; color: var(--text-primary);">Welcome to NutriMind!</h2>
        </div>
        <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 1.5rem;">
            Your AI-powered nutrition assistant that helps you track, analyze, and optimize your health journey.
            Get personalized insights and recommendations based on your unique profile.
        </p>
        
        <div class="grid-container">
            <div class="grid-item">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📸</div>
                <h4 style="margin: 0; color: var(--text-primary);">AI Food Scanner</h4>
                <p style="color: var(--text-secondary); font-size: 0.875rem; margin: 0.25rem 0 0;">
                    Upload food photos for instant nutrition analysis
                </p>
            </div>
            <div class="grid-item">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊</div>
                <h4 style="margin: 0; color: var(--text-primary);">Smart Tracking</h4>
                <p style="color: var(--text-secondary); font-size: 0.875rem; margin: 0.25rem 0 0;">
                    Track your food intake and exercise with detailed analytics
                </p>
            </div>
            <div class="grid-item">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🥗</div>
                <h4 style="margin: 0; color: var(--text-primary);">Personalized Recommendations</h4>
                <p style="color: var(--text-secondary); font-size: 0.875rem; margin: 0.25rem 0 0;">
                    Get meal suggestions based on your diet preference
                </p>
            </div>
        </div>
        
        <p style="color: var(--text-muted); text-align: center; font-style: italic; margin-top: 2rem;">
            Create a profile or use Demo Mode to get started!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**AI Food Scanner**\n\nUpload food photos for instant nutrition analysis.")
    
    with col2:
        st.info("**Smart Tracking**\n\nTrack your food intake and exercise with detailed analytics.")
    
    with col3:
        st.info("**Personalized Recommendations**\n\nGet meal suggestions based on your diet preference.")
    
else:
    # Show success message if food was saved
    if st.session_state.show_success:
        st.markdown(f"""
        <div class="success-toast-pro">
            <div style="font-size: 1.5rem;">🎉</div>
            <div>
                <strong>Success!</strong><br>
                <small>{st.session_state.success_message}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.session_state.show_success = False
    
    st.markdown(f"""
    <div class="pro-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="margin: 0; color: var(--text-primary);">👋 Welcome, {st.session_state.user['name']}!</h2>
                <p style="color: var(--text-secondary); margin: 0.25rem 0 0;">
                    Here's your nutrition overview for {datetime.now().strftime('%A, %B %d')}
                </p>
            </div>
            <div style="display: flex; gap: 0.5rem;">
                <div style="background: var(--primary); color: white; padding: 0.5rem 1rem; border-radius: 8px; font-weight: 500;">
                    {datetime.now().strftime('%I:%M %p')}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs with professional styling
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📝 Log Food", "🏋️ Exercise", "🥗 Recommendations"])
    
    # ... [Keep all the existing tab content from your original code here]
    # Make sure to copy the entire content for tab1, tab2, tab3, tab4 from your original code
    # This includes the dashboard, log food, exercise, and recommendations sections

# ========== FOOTER ==========
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #00C9C9; padding: 20px;">
        <p><strong>NutriMind</strong> | Scan.Track.Grow 🥗🧠🏃💪</p>
        <p><strong>Built for Google TechSprint</strong></p>
        <p style="font-size: 0.9em;">Team euphoria</p>
    </div>
    """,
    unsafe_allow_html=True
)
