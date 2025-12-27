# app.py - NutriMind Professional UI
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
import math

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="NutriMind | AI Nutrition Assistant",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== PROFESSIONAL CSS ==========
st.markdown("""
<style>
    /* Import Inter Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    :root {
        --primary: #10B981;
        --primary-dark: #059669;
        --primary-light: #D1FAE5;
        --secondary: #3B82F6;
        --accent: #8B5CF6;
        --text: #1F2937;
        --text-light: #6B7280;
        --bg: #F9FAFB;
        --card: #FFFFFF;
        --border: #E5E7EB;
        --success: #10B981;
        --warning: #F59E0B;
        --danger: #EF4444;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --radius: 12px;
    }
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: var(--bg);
    }
    
    /* Custom Header */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }
    
    .subheader {
        color: var(--text-light);
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Modern Cards */
    .card {
        background: var(--card);
        border-radius: var(--radius);
        padding: 1.5rem;
        border: 1px solid var(--border);
        box-shadow: var(--shadow);
        transition: transform 0.2s, box-shadow 0.2s;
        margin-bottom: 1rem;
    }
    
    .card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    .card-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1rem;
    }
    
    .card-icon {
        width: 40px;
        height: 40px;
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.25rem;
    }
    
    /* Stats Cards */
    .stat-card {
        background: var(--card);
        border-radius: var(--radius);
        padding: 1.25rem;
        text-align: center;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text);
        margin: 0.5rem 0;
    }
    
    .stat-label {
        color: var(--text-light);
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    /* Progress Bars */
    .progress-container {
        background: var(--border);
        border-radius: 100px;
        height: 8px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        border-radius: 100px;
        transition: width 0.5s ease;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s;
        box-shadow: var(--shadow);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-lg);
    }
    
    .secondary-btn {
        background: white !important;
        color: var(--primary) !important;
        border: 2px solid var(--primary) !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--card);
        border-right: 1px solid var(--border);
    }
    
    .sidebar-header {
        padding: 2rem 1.5rem 1rem;
        border-bottom: 1px solid var(--border);
    }
    
    .nav-item {
        padding: 0.75rem 1.5rem;
        margin: 0.25rem 0;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        cursor: pointer;
        transition: all 0.2s;
        color: var(--text-light);
        font-weight: 500;
    }
    
    .nav-item:hover {
        background: var(--primary-light);
        color: var(--primary);
    }
    
    .nav-item.active {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        box-shadow: var(--shadow);
    }
    
    /* Food Log Items */
    .food-item {
        background: var(--card);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid var(--primary);
        border: 1px solid var(--border);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Success Toast */
    .success-toast {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: var(--radius);
        margin: 1rem 0;
        animation: slideIn 0.3s ease;
        box-shadow: var(--shadow-lg);
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Metrics Styling */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 700 !important;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: var(--card) !important;
        border-radius: 8px !important;
        border: 1px solid var(--border) !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border-color: var(--primary) !important;
    }
</style>
""", unsafe_allow_html=True)

# ========== SESSION STATE ==========
if 'page' not in st.session_state:
    st.session_state.page = "dashboard"
    
if 'user' not in st.session_state:
    st.session_state.user = {
        'name': 'Alex Johnson',
        'age': 28,
        'weight': 70,
        'height': 175,
        'gender': 'Male',
        'activity': 'Moderate'
    }

if 'food_logs' not in st.session_state:
    st.session_state.food_logs = [
        {'name': 'Avocado Toast', 'calories': 320, 'protein': 12, 'carbs': 35, 'fats': 18, 'time': '08:30'},
        {'name': 'Grilled Chicken Salad', 'calories': 420, 'protein': 35, 'carbs': 12, 'fats': 22, 'time': '13:00'},
        {'name': 'Protein Shake', 'calories': 180, 'protein': 25, 'carbs': 8, 'fats': 3, 'time': '16:30'}
    ]

if 'exercise_logs' not in st.session_state:
    st.session_state.exercise_logs = [
        {'name': 'Morning Run', 'duration': 30, 'calories': 320, 'time': '07:00'},
        {'name': 'Weight Training', 'duration': 45, 'calories': 280, 'time': '18:00'}
    ]

if 'daily_totals' not in st.session_state:
    st.session_state.daily_totals = {
        'calories': 920,
        'protein': 72,
        'carbs': 55,
        'fats': 43,
        'calories_burned': 600,
        'water': 1500
    }

if 'goals' not in st.session_state:
    st.session_state.goals = {
        'calories': 2200,
        'protein': 120,
        'carbs': 250,
        'fats': 70,
        'exercise': 45,
        'water': 3000
    }

# ========== BACKEND FUNCTIONS ==========
def analyze_food_with_gemini(food_input, image=None):
    """AI Food Analysis"""
    api_key = "AIzaSyCUFEN7loZiJxffZfG3AubcIRarpigeGUY"
    
    with st.spinner("🔍 Analyzing with AI..."):
        try:
            if image:
                buffered = io.BytesIO()
                image.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": "Analyze food nutrition and return JSON with calories, protein, carbs, fats"},
                            {"inline_data": {"mime_type": "image/jpeg", "data": img_str}}
                        ]
                    }],
                    "generationConfig": {"temperature": 0.1}
                }
            else:
                payload = {
                    "contents": [{
                        "parts": [{"text": f"Analyze {food_input} nutrition. Return JSON: food_name, calories, protein, carbs, fats"}]
                    }],
                    "generationConfig": {"temperature": 0.1}
                }
            
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={api_key}",
                json=payload,
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text']
                text = text.strip().replace('```json', '').replace('```', '')
                
                try:
                    data = json.loads(text)
                    return {
                        'name': data.get('food_name', food_input),
                        'calories': int(data.get('calories', 300)),
                        'protein': int(data.get('protein', 15)),
                        'carbs': int(data.get('carbs', 40)),
                        'fats': int(data.get('fats', 10))
                    }
                except:
                    pass
        except:
            pass
        
        # Fallback
        food_db = {
            'pizza': {'name': 'Pizza Slice', 'calories': 285, 'protein': 12, 'carbs': 36, 'fats': 10},
            'salad': {'name': 'Chicken Salad', 'calories': 320, 'protein': 35, 'carbs': 12, 'fats': 15},
            'smoothie': {'name': 'Fruit Smoothie', 'calories': 200, 'protein': 8, 'carbs': 30, 'fats': 5},
            'rice': {'name': 'Steamed Rice', 'calories': 205, 'protein': 4, 'carbs': 45, 'fats': 0.4},
            'chicken': {'name': 'Grilled Chicken', 'calories': 165, 'protein': 31, 'carbs': 0, 'fats': 3.6},
            'egg': {'name': 'Boiled Eggs', 'calories': 155, 'protein': 12, 'carbs': 1, 'fats': 11},
            'dosa': {'name': 'Masala Dosa', 'calories': 200, 'protein': 4, 'carbs': 30, 'fats': 6}
        }
        
        for key, value in food_db.items():
            if key in food_input.lower():
                return value
        
        return {
            'name': food_input.title(),
            'calories': random.randint(200, 500),
            'protein': random.randint(10, 30),
            'carbs': random.randint(20, 60),
            'fats': random.randint(5, 25)
        }

def calculate_progress(value, goal):
    return min(100, (value / goal) * 100) if goal > 0 else 0

def get_meal_suggestions():
    suggestions = {
        'breakfast': [
            {'name': 'Avocado Toast', 'calories': 320, 'protein': 12, 'carbs': 35, 'fats': 18},
            {'name': 'Greek Yogurt Bowl', 'calories': 280, 'protein': 20, 'carbs': 30, 'fats': 8},
            {'name': 'Protein Oatmeal', 'calories': 350, 'protein': 25, 'carbs': 45, 'fats': 6}
        ],
        'lunch': [
            {'name': 'Grilled Chicken Salad', 'calories': 420, 'protein': 35, 'carbs': 12, 'fats': 22},
            {'name': 'Quinoa Buddha Bowl', 'calories': 380, 'protein': 18, 'carbs': 55, 'fats': 12},
            {'name': 'Turkey Wrap', 'calories': 320, 'protein': 22, 'carbs': 30, 'fats': 14}
        ],
        'dinner': [
            {'name': 'Salmon with Veggies', 'calories': 450, 'protein': 40, 'carbs': 20, 'fats': 25},
            {'name': 'Chicken Stir Fry', 'calories': 380, 'protein': 32, 'carbs': 25, 'fats': 18},
            {'name': 'Lentil Curry', 'calories': 320, 'protein': 18, 'carbs': 45, 'fats': 8}
        ]
    }
    return suggestions

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h1 style="font-size: 1.75rem; font-weight: 800; margin: 0; background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🥗 NutriMind
        </h1>
        <p style="color: var(--text-light); margin: 0.25rem 0 0; font-size: 0.875rem;">
            AI Nutrition Assistant
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="padding: 1.5rem;">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.5rem;">
            <div style="width: 48px; height: 48px; background: linear-gradient(135deg, var(--primary), var(--secondary)); border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 1.25rem;">
                👤
            </div>
            <div>
                <div style="font-weight: 600; color: var(--text);">{name}</div>
                <div style="font-size: 0.875rem; color: var(--text-light);">Premium Member</div>
            </div>
        </div>
    """.format(name=st.session_state.user['name']), unsafe_allow_html=True)
    
    # Navigation
    nav_items = [
        ("📊", "Dashboard", "dashboard"),
        ("📝", "Log Food", "log_food"),
        ("🏃", "Exercise", "exercise"),
        ("🥗", "Meal Plans", "meals"),
        ("📈", "Analytics", "analytics"),
        ("⚙️", "Settings", "settings")
    ]
    
    for icon, label, key in nav_items:
        is_active = st.session_state.page == key
        st.markdown(f"""
        <div class="nav-item {'active' if is_active else ''}" onclick="window.location.href='?page={key}'">
            <span style="font-size: 1.25rem;">{icon}</span>
            <span>{label}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Daily Stats
    st.markdown("""
    <div style="background: var(--primary-light); border-radius: var(--radius); padding: 1rem; margin: 1.5rem; border: 1px solid var(--border);">
        <div style="font-size: 0.875rem; color: var(--text-light); margin-bottom: 0.5rem;">Today's Progress</div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-size: 1.5rem; font-weight: 700; color: var(--text);">
                    {calories}/{goal}
                </div>
                <div style="font-size: 0.75rem; color: var(--text-light);">Calories</div>
            </div>
            <div style="width: 60px; height: 60px;">
                <div style="width: 60px; height: 60px; border-radius: 50%; background: conic-gradient(var(--primary) {percent}%, var(--border) 0%); display: flex; align-items: center; justify-content: center;">
                    <div style="width: 50px; height: 50px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; color: var(--text);">
                        {percent}%
                    </div>
                </div>
            </div>
        </div>
    </div>
    """.format(
        calories=st.session_state.daily_totals['calories'],
        goal=st.session_state.goals['calories'],
        percent=int(calculate_progress(st.session_state.daily_totals['calories'], st.session_state.goals['calories']))
    ), unsafe_allow_html=True)

# ========== DASHBOARD PAGE ==========
if st.session_state.page == "dashboard":
    # Header
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        st.markdown(f'<div class="main-header">Welcome back, {st.session_state.user["name"]}!</div>', unsafe_allow_html=True)
        st.markdown('<div class="subheader">Here\'s your nutrition summary for today</div>', unsafe_allow_html=True)
    
    with col3:
        st.write("")  # Spacer
        st.write("")  # Spacer
        if st.button("📸 Scan Food", use_container_width=True):
            st.session_state.page = "log_food"
            st.rerun()
    
    # Stats Cards
    st.markdown("### Daily Metrics")
    
    calories_progress = calculate_progress(st.session_state.daily_totals['calories'], st.session_state.goals['calories'])
    protein_progress = calculate_progress(st.session_state.daily_totals['protein'], st.session_state.goals['protein'])
    water_progress = calculate_progress(st.session_state.daily_totals['water'], st.session_state.goals['water'])
    exercise_progress = calculate_progress(st.session_state.exercise_logs[-1]['duration'] if st.session_state.exercise_logs else 0, st.session_state.goals['exercise'])
    
    cols = st.columns(4)
    with cols[0]:
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size: 1.25rem;">🔥</div>
            <div class="stat-value">{st.session_state.daily_totals['calories']}</div>
            <div class="stat-label">Calories</div>
            <div class="progress-container">
                <div class="progress-bar" style="width: {calories_progress}%"></div>
            </div>
            <div style="font-size: 0.75rem; color: var(--text-light); margin-top: 0.25rem;">
                {st.session_state.daily_totals['calories']}/{st.session_state.goals['calories']}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size: 1.25rem;">💪</div>
            <div class="stat-value">{st.session_state.daily_totals['protein']}g</div>
            <div class="stat-label">Protein</div>
            <div class="progress-container">
                <div class="progress-bar" style="width: {protein_progress}%"></div>
            </div>
            <div style="font-size: 0.75rem; color: var(--text-light); margin-top: 0.25rem;">
                {st.session_state.daily_totals['protein']}/{st.session_state.goals['protein']}g
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size: 1.25rem;">💧</div>
            <div class="stat-value">{st.session_state.daily_totals['water']}ml</div>
            <div class="stat-label">Water</div>
            <div class="progress-container">
                <div class="progress-bar" style="width: {water_progress}%"></div>
            </div>
            <div style="font-size: 0.75rem; color: var(--text-light); margin-top: 0.25rem;">
                {st.session_state.daily_totals['water']}/{st.session_state.goals['water']}ml
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with cols[3]:
        exercise_minutes = sum([ex['duration'] for ex in st.session_state.exercise_logs])
        st.markdown(f"""
        <div class="stat-card">
            <div style="font-size: 1.25rem;">🏃</div>
            <div class="stat-value">{exercise_minutes}min</div>
            <div class="stat-label">Exercise</div>
            <div class="progress-container">
                <div class="progress-bar" style="width: {exercise_progress}%"></div>
            </div>
            <div style="font-size: 0.75rem; color: var(--text-light); margin-top: 0.25rem;">
                {exercise_minutes}/{st.session_state.goals['exercise']}min
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Charts and Logs
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <div class="card-icon">📈</div>
                <h3 style="margin: 0; color: var(--text);">Nutrition Breakdown</h3>
            </div>
        """, unsafe_allow_html=True)
        
        # Pie chart for macros
        fig = px.pie(
            values=[
                st.session_state.daily_totals['protein'] * 4,
                st.session_state.daily_totals['carbs'] * 4,
                st.session_state.daily_totals['fats'] * 9
            ],
            names=['Protein', 'Carbs', 'Fats'],
            color=['Protein', 'Carbs', 'Fats'],
            color_discrete_map={'Protein': '#10B981', 'Carbs': '#3B82F6', 'Fats': '#8B5CF6'}
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(showlegend=False, height=300, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <div class="card-icon">🍽️</div>
                <h3 style="margin: 0; color: var(--text);">Recent Meals</h3>
            </div>
        """, unsafe_allow_html=True)
        
        for food in st.session_state.food_logs[-3:]:
            st.markdown(f"""
            <div class="food-item">
                <div>
                    <div style="font-weight: 600; color: var(--text);">{food['name']}</div>
                    <div style="font-size: 0.875rem; color: var(--text-light);">
                        🔥 {food['calories']}cal • 💪 {food['protein']}g • 🕐 {food['time']}
                    </div>
                </div>
                <div style="font-size: 0.875rem; color: var(--text-light);">
                    {food['calories']} cal
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("+ Add Meal", key="add_meal_dash", use_container_width=True):
            st.session_state.page = "log_food"
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Exercise Section
    st.markdown("""
    <div class="card">
        <div class="card-header">
            <div class="card-icon">🏃</div>
            <h3 style="margin: 0; color: var(--text);">Today's Exercise</h3>
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.exercise_logs:
        for ex in st.session_state.exercise_logs:
            st.markdown(f"""
            <div class="food-item">
                <div>
                    <div style="font-weight: 600; color: var(--text);">{ex['name']}</div>
                    <div style="font-size: 0.875rem; color: var(--text-light);">
                        ⏱️ {ex['duration']}min • 🔥 {ex['calories']}cal • 🕐 {ex['time']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown('<p style="color: var(--text-light); text-align: center; padding: 2rem;">No exercise logged today</p>', unsafe_allow_html=True)
    
    if st.button("+ Log Exercise", key="log_exercise_dash", use_container_width=True):
        st.session_state.page = "exercise"
        st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# ========== LOG FOOD PAGE ==========
elif st.session_state.page == "log_food":
    st.markdown('<div class="main-header">Log Food</div>', unsafe_allow_html=True)
    st.markdown('<div class="subheader">Scan, upload, or manually enter your meal</div>', unsafe_allow_html=True)
    
    # Back button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()
    
    # Tabs for different methods
    tab1, tab2, tab3 = st.tabs(["📷 Camera Scan", "📁 Upload Image", "✍️ Manual Entry"])
    
    with tab1:
        st.markdown("""
        <div class="card">
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">📸</div>
                <h3 style="color: var(--text);">Camera Scan</h3>
                <p style="color: var(--text-light);">Take a photo of your meal for instant AI analysis</p>
                <div style="margin-top: 2rem;">
        """, unsafe_allow_html=True)
        
        # Camera input placeholder
        uploaded_file = st.camera_input("Take a photo of your food", label_visibility="collapsed")
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            with st.spinner("Analyzing food..."):
                time.sleep(2)  # Simulate AI processing
                result = analyze_food_with_gemini("food", image)
                
                st.markdown(f"""
                <div class="card" style="margin-top: 1rem;">
                    <h4 style="color: var(--text); margin-bottom: 1rem;">{result['name']}</h4>
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem;">
                        <div style="text-align: center;">
                            <div style="font-size: 1.5rem; font-weight: 700; color: var(--text);">{result['calories']}</div>
                            <div style="font-size: 0.875rem; color: var(--text-light);">Calories</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 1.5rem; font-weight: 700; color: var(--text);">{result['protein']}g</div>
                            <div style="font-size: 0.875rem; color: var(--text-light);">Protein</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 1.5rem; font-weight: 700; color: var(--text);">{result['carbs']}g</div>
                            <div style="font-size: 0.875rem; color: var(--text-light);">Carbs</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 1.5rem; font-weight: 700; color: var(--text);">{result['fats']}g</div>
                            <div style="font-size: 0.875rem; color: var(--text-light);">Fats</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("✅ Save Meal", use_container_width=True, type="primary"):
                    result['time'] = datetime.now().strftime("%H:%M")
                    st.session_state.food_logs.append(result)
                    st.session_state.daily_totals['calories'] += result['calories']
                    st.session_state.daily_totals['protein'] += result['protein']
                    st.session_state.daily_totals['carbs'] += result['carbs']
                    st.session_state.daily_totals['fats'] += result['fats']
                    st.success("Meal saved successfully!")
                    time.sleep(1)
                    st.session_state.page = "dashboard"
                    st.rerun()
        
        st.markdown("</div></div></div>", unsafe_allow_html=True)
    
    with tab2:
        st.markdown("""
        <div class="card">
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">📁</div>
                <h3 style="color: var(--text);">Upload Image</h3>
                <p style="color: var(--text-light);">Upload a photo of your meal or food label</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
        
        if uploaded:
            image = Image.open(uploaded)
            st.image(image, width=300)
            
            if st.button("Analyze Image", use_container_width=True):
                with st.spinner("Analyzing..."):
                    result = analyze_food_with_gemini("food", image)
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Calories", result['calories'])
                    col2.metric("Protein", f"{result['protein']}g")
                    col3.metric("Carbs", f"{result['carbs']}g")
                    col4.metric("Fats", f"{result['fats']}g")
    
    with tab3:
        st.markdown("""
        <div class="card">
            <div style="text-align: center; padding: 2rem;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">✍️</div>
                <h3 style="color: var(--text);">Manual Entry</h3>
                <p style="color: var(--text-light);">Enter food details manually</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            food_name = st.text_input("Food Name", placeholder="e.g., Masala Dosa, Pizza, Salad")
            calories = st.number_input("Calories", min_value=0, value=300)
            protein = st.number_input("Protein (g)", min_value=0, value=15)
        
        with col2:
            carbs = st.number_input("Carbs (g)", min_value=0, value=40)
            fats = st.number_input("Fats (g)", min_value=0, value=10)
            portion = st.select_slider("Portion Size", ["Small", "Medium", "Large"], value="Medium")
        
        if st.button("Save Manual Entry", use_container_width=True, type="primary"):
            food_data = {
                'name': food_name or "Custom Meal",
                'calories': calories,
                'protein': protein,
                'carbs': carbs,
                'fats': fats,
                'time': datetime.now().strftime("%H:%M")
            }
            st.session_state.food_logs.append(food_data)
            st.session_state.daily_totals['calories'] += calories
            st.session_state.daily_totals['protein'] += protein
            st.session_state.daily_totals['carbs'] += carbs
            st.session_state.daily_totals['fats'] += fats
            st.success("Meal saved!")
            time.sleep(1)
            st.session_state.page = "dashboard"
            st.rerun()

# ========== EXERCISE PAGE ==========
elif st.session_state.page == "exercise":
    st.markdown('<div class="main-header">Exercise Tracking</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.page = "dashboard"
            st.rerun()
    
    # Exercise log form
    with st.form("exercise_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            exercise_type = st.selectbox("Exercise Type", [
                "Running", "Walking", "Cycling", "Swimming", 
                "Weight Training", "Yoga", "HIIT", "Other"
            ])
            duration = st.slider("Duration (minutes)", 5, 180, 30)
        
        with col2:
            intensity = st.select_slider("Intensity", ["Light", "Moderate", "Hard", "Very Hard"])
            calories = duration * {
                "Light": 5, "Moderate": 8, "Hard": 12, "Very Hard": 15
            }[intensity]
            
            st.metric("Estimated Calories", f"{calories}")
        
        if st.form_submit_button("Log Exercise", type="primary"):
            exercise_data = {
                'name': exercise_type,
                'duration': duration,
                'calories': calories,
                'time': datetime.now().strftime("%H:%M")
            }
            st.session_state.exercise_logs.append(exercise_data)
            st.session_state.daily_totals['calories_burned'] += calories
            st.success("Exercise logged!")
            time.sleep(1)
            st.session_state.page = "dashboard"
            st.rerun()

# ========== MEAL PLANS PAGE ==========
elif st.session_state.page == "meals":
    st.markdown('<div class="main-header">Meal Recommendations</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.page = "dashboard"
            st.rerun()
    
    # Diet type selection
    diet_type = st.radio("Select Diet Preference:", 
                        ["🥗 Vegetarian", "🍗 Non-Vegetarian", "🥚 Eggetarian"],
                        horizontal=True)
    
    # Meal time selection
    meal_time = st.selectbox("Meal Time", ["Breakfast", "Lunch", "Dinner", "Snacks"])
    
    # Get suggestions
    suggestions = get_meal_suggestions()[meal_time.lower()]
    
    # Display suggestions
    st.markdown(f"### {meal_time} Suggestions")
    
    cols = st.columns(3)
    for idx, meal in enumerate(suggestions):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="card">
                <h4 style="color: var(--text); margin-bottom: 0.5rem;">{meal['name']}</h4>
                <div style="display: flex; gap: 1rem; margin-bottom: 1rem;">
                    <div style="font-size: 0.875rem; color: var(--text-light);">
                        🔥 {meal['calories']} cal
                    </div>
                    <div style="font-size: 0.875rem; color: var(--text-light);">
                        💪 {meal['protein']}g
                    </div>
                </div>
                <button onclick="addMeal({idx})" style="width: 100%; padding: 0.5rem; background: var(--primary); color: white; border: none; border-radius: 6px; cursor: pointer;">
                    Add to Log
                </button>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Add {meal['name']}", key=f"add_meal_{idx}", use_container_width=True):
                meal['time'] = datetime.now().strftime("%H:%M")
                st.session_state.food_logs.append(meal)
                st.session_state.daily_totals['calories'] += meal['calories']
                st.session_state.daily_totals['protein'] += meal['protein']
                st.session_state.daily_totals['carbs'] += meal['carbs']
                st.session_state.daily_totals['fats'] += meal['fats']
                st.success(f"Added {meal['name']}!")
                time.sleep(1)
                st.rerun()

# ========== ANALYTICS PAGE ==========
elif st.session_state.page == "analytics":
    st.markdown('<div class="main-header">Nutrition Analytics</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.page = "dashboard"
            st.rerun()
    
    # Weekly data
    dates = pd.date_range(end=datetime.now(), periods=7).strftime('%b %d').tolist()
    calories_data = [random.randint(1800, 2500) for _ in range(7)]
    protein_data = [random.randint(80, 150) for _ in range(7)]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Weekly Calories")
        fig = px.line(
            x=dates,
            y=calories_data,
            markers=True,
            line_shape='spline'
        )
        fig.update_layout(
            height=300,
            margin=dict(t=0, b=0, l=0, r=0),
            xaxis_title=None,
            yaxis_title="Calories",
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Weekly Protein")
        fig = px.bar(
            x=dates,
            y=protein_data,
            color=protein_data,
            color_continuous_scale=['#D1FAE5', '#10B981']
        )
        fig.update_layout(
            height=300,
            margin=dict(t=0, b=0, l=0, r=0),
            xaxis_title=None,
            yaxis_title="Protein (g)",
            plot_bgcolor='white',
            paper_bgcolor='white',
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

# ========== SETTINGS PAGE ==========
elif st.session_state.page == "settings":
    st.markdown('<div class="main-header">Settings</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.page = "dashboard"
            st.rerun()
    
    with st.form("settings_form"):
        st.markdown("### Personal Information")
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", value=st.session_state.user['name'])
            age = st.number_input("Age", 1, 100, value=st.session_state.user['age'])
        
        with col2:
            weight = st.number_input("Weight (kg)", 30, 200, value=st.session_state.user['weight'])
            height = st.number_input("Height (cm)", 100, 250, value=st.session_state.user['height'])
        
        st.markdown("### Daily Goals")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            calorie_goal = st.number_input("Calorie Goal", 1000, 5000, value=st.session_state.goals['calories'])
        with col2:
            protein_goal = st.number_input("Protein Goal (g)", 30, 300, value=st.session_state.goals['protein'])
        with col3:
            water_goal = st.number_input("Water Goal (ml)", 1000, 5000, value=st.session_state.goals['water'])
        
        if st.form_submit_button("Save Settings", type="primary"):
            st.session_state.user.update({
                'name': name,
                'age': age,
                'weight': weight,
                'height': height
            })
            st.session_state.goals.update({
                'calories': calorie_goal,
                'protein': protein_goal,
                'water': water_goal
            })
            st.success("Settings saved successfully!")

# ========== FOOTER ==========
st.markdown("""
<div style="text-align: center; color: var(--text-light); padding: 2rem; margin-top: 2rem; border-top: 1px solid var(--border);">
    <p style="margin: 0.5rem 0;"><strong>NutriMind</strong>|Scan.Track.Grow 🥗🧠🏃🏽‍♀️💪🏽</p>
    <p style="margin: 0.5rem 0; font-size: 0.875rem;">Built for Google TechSprint by Team euphoria</p>
</div>
""", unsafe_allow_html=True)
