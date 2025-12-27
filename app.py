# app.py - NutriMind Modern React-Style UI
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

# ========== INITIALIZE SESSION STATE ==========
if 'page' not in st.session_state:
    st.session_state.page = "landing"
    
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

# Configure page
st.set_page_config(
    page_title="NutriMind - AI Nutrition Assistant",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== MODERN REACT-STYLE CSS ==========
st.markdown("""
<style>
    /* === MODERN HEALTH THEME === */
    :root {
        --primary: #00B894;
        --primary-dark: #00A08A;
        --accent: #00FFD4;
        --secondary: #0984E3;
        --light: #E8FFF7;
        --background: #F8FDFC;
        --card: #FFFFFF;
        --text: #2D3436;
        --text-light: #636E72;
        --border: #E0E0E0;
        --error: #D63031;
        --warning: #FDCB6E;
        --success: #00B894;
        --shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        --shadow-hover: 0 8px 30px rgba(0, 184, 148, 0.15);
    }
    
    /* Main App */
    .stApp {
        background: var(--background);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Modern Header */
    .modern-header {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin: 2rem 0 1rem;
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.5px;
    }
    
    /* Cards */
    .modern-card {
        background: var(--card);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: var(--shadow);
        border: 1px solid var(--border);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .modern-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-hover);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 28px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.2s !important;
        box-shadow: 0 4px 12px rgba(0, 184, 148, 0.2) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0, 184, 148, 0.3) !important;
    }
    
    /* Secondary Button */
    .secondary-btn {
        background: white !important;
        color: var(--primary) !important;
        border: 2px solid var(--primary) !important;
    }
    
    /* Stats Cards */
    .stat-card {
        background: var(--card);
        border-radius: 16px;
        padding: 20px;
        border-left: 6px solid var(--primary);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    
    .stat-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        margin: 0 auto 12px;
    }
    
    /* Progress Bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--primary), var(--accent)) !important;
        border-radius: 10px !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: var(--card) !important;
        border-radius: 12px 12px 0 0 !important;
        border: 1px solid var(--border) !important;
        padding: 12px 24px !important;
        font-weight: 500 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        border-bottom: 3px solid var(--accent) !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background: var(--card) !important;
        border: 2px solid var(--border) !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
    }
    
    /* Metrics */
    .stMetric {
        background: var(--card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: var(--shadow) !important;
    }
    
    /* Success Toast */
    .success-toast {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
        padding: 16px 24px !important;
        border-radius: 12px !important;
        margin: 16px 0 !important;
        animation: slideIn 0.3s ease !important;
        box-shadow: 0 8px 24px rgba(0, 184, 148, 0.3) !important;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Navigation Sidebar */
    [data-testid="stSidebar"] {
        background: var(--card) !important;
        border-right: 1px solid var(--border) !important;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Mobile Responsive */
    @media (max-width: 768px) {
        .modern-header {
            font-size: 2rem;
        }
        .modern-card {
            padding: 16px;
        }
    }
</style>
""", unsafe_allow_html=True)

# ========== BACKEND FUNCTIONS (KEEP YOUR EXISTING LOGIC) ==========
def analyze_food_with_gemini(food_input, image=None):
    """PROPER Gemini AI Analysis"""
    api_key = "AIzaSyCUFEN7loZiJxffZfG3AubcIRarpigeGUY"
    
    thinking_placeholder = st.empty()
    thinking_placeholder.markdown('<div class="modern-card">🤖 AI is analyzing your food...</div>', unsafe_allow_html=True)
    
    try:
        if not api_key or "AIzaSy" not in api_key:
            thinking_placeholder.empty()
            st.error("❌ Invalid API key")
            return get_fallback_nutrition(food_input)
        
        if image:
            buffered = io.BytesIO()
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(buffered, format="JPEG", quality=90)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            prompt = """You are a nutrition expert. Analyze this food image.
            Return ONLY JSON: {"food_name": "...", "calories": number, "protein": number, "carbs": number, "fats": number, "insight": "..."}"""
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": img_str
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 500,
                }
            }
        else:
            prompt = f"""Analyze this food: {food_input}
            Return ONLY JSON: {{"food_name": "...", "calories": number, "protein": number, "carbs": number, "fats": number, "insight": "..."}}"""
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 500,
                }
            }
        
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={api_key}",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        thinking_placeholder.empty()
        
        if response.status_code == 200:
            result = response.json()
            if "candidates" in result and len(result["candidates"]) > 0:
                response_text = result["candidates"][0]["content"]["parts"][0]["text"]
                response_text = response_text.strip()
                
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    try:
                        nutrition_data = json.loads(json_match.group())
                        if "food_name" in nutrition_data:
                            required_fields = ["calories", "protein", "carbs", "fats", "insight"]
                            for field in required_fields:
                                if field not in nutrition_data:
                                    if field == "insight":
                                        nutrition_data[field] = "Nutrition information provided by AI"
                                    else:
                                        nutrition_data[field] = 0
                            
                            for field in ["calories", "protein", "carbs", "fats"]:
                                try:
                                    nutrition_data[field] = int(float(nutrition_data[field]))
                                except:
                                    nutrition_data[field] = 0
                            
                            st.success(f"✅ AI Detected: **{nutrition_data['food_name']}**")
                            return nutrition_data
                    except json.JSONDecodeError:
                        st.warning("⚠️ Could not parse AI response")
        
        if response.status_code == 403:
            st.error("❌ API key invalid. Get new one: https://makersuite.google.com/app/apikey")
        elif response.status_code == 429:
            st.error("❌ API quota exceeded. Try again later.")
        else:
            st.warning(f"⚠️ API Error {response.status_code}")
        
        return get_fallback_nutrition(food_input)
        
    except requests.exceptions.Timeout:
        thinking_placeholder.empty()
        st.warning("⚠️ AI analysis timed out")
        return get_fallback_nutrition(food_input)
    except Exception as e:
        thinking_placeholder.empty()
        st.warning(f"⚠️ Error: {str(e)[:100]}")
        return get_fallback_nutrition(food_input)

def get_fallback_nutrition(food_name):
    """Fallback nutrition database"""
    food_db = {
        "dosa": {"food_name": "Masala Dosa", "calories": 200, "protein": 4, "carbs": 30, "fats": 6},
        "idli": {"food_name": "Idli", "calories": 60, "protein": 2, "carbs": 12, "fats": 0.5},
        "poha": {"food_name": "Poha", "calories": 250, "protein": 6, "carbs": 45, "fats": 5},
        "chapati": {"food_name": "Chapati", "calories": 70, "protein": 3, "carbs": 15, "fats": 0.4},
        "rice": {"food_name": "Steamed Rice", "calories": 205, "protein": 4.3, "carbs": 45, "fats": 0.4},
        "biryani": {"food_name": "Chicken Biryani", "calories": 500, "protein": 25, "carbs": 60, "fats": 20},
        "butter chicken": {"food_name": "Butter Chicken", "calories": 450, "protein": 30, "carbs": 15, "fats": 30},
        "paneer butter": {"food_name": "Paneer Butter Masala", "calories": 400, "protein": 22, "carbs": 20, "fats": 25},
        "dal": {"food_name": "Dal Tadka", "calories": 150, "protein": 9, "carbs": 22, "fats": 4},
        "banana": {"food_name": "Banana", "calories": 105, "protein": 1.3, "carbs": 27, "fats": 0.3},
        "apple": {"food_name": "Apple", "calories": 95, "protein": 0.5, "carbs": 25, "fats": 0.3},
        "egg": {"food_name": "Egg (Boiled)", "calories": 78, "protein": 6, "carbs": 0.6, "fats": 5},
        "chicken": {"food_name": "Chicken Breast", "calories": 165, "protein": 31, "carbs": 0, "fats": 3.6},
        "pizza": {"food_name": "Pizza Slice", "calories": 285, "protein": 12, "carbs": 36, "fats": 10},
        "burger": {"food_name": "Cheese Burger", "calories": 354, "protein": 15, "carbs": 29, "fats": 20},
    }
    
    if not food_name:
        return {
            "food_name": "Food Item",
            "calories": 250,
            "protein": 12,
            "carbs": 30,
            "fats": 8,
            "insight": "General food item"
        }
    
    food_lower = food_name.lower()
    for key in food_db:
        if key in food_lower:
            food_db[key]["insight"] = "From nutrition database"
            return food_db[key]
    
    return {
        "food_name": food_name.title(),
        "calories": random.randint(150, 400),
        "protein": random.randint(5, 25),
        "carbs": random.randint(15, 50),
        "fats": random.randint(5, 20),
        "insight": "Estimated nutrition values"
    }

def get_exercise_suggestions(calories_consumed):
    """Get exercise suggestions"""
    exercises = [
        {"name": "Running (8 km/h)", "duration": 30, "calories_per_min": 10},
        {"name": "Cycling (moderate)", "duration": 45, "calories_per_min": 7},
        {"name": "Swimming", "duration": 40, "calories_per_min": 8},
        {"name": "Jumping Rope", "duration": 20, "calories_per_min": 12},
        {"name": "Yoga", "duration": 60, "calories_per_min": 4},
        {"name": "Walking (brisk)", "duration": 60, "calories_per_min": 5},
    ]
    
    adjusted_exercises = []
    for ex in exercises:
        target_calories = calories_consumed * 0.3
        adjusted_duration = min(120, int(target_calories / ex['calories_per_min']))
        if adjusted_duration > 10:
            adjusted_exercises.append({
                "name": ex['name'],
                "duration": adjusted_duration,
                "calories_per_min": ex['calories_per_min']
            })
    
    return adjusted_exercises[:4]

def calculate_calorie_target(age, gender, activity_level="moderate"):
    if gender == "Male":
        bmr = 10 * 70 + 6.25 * 170 - 5 * age + 5
    else:
        bmr = 10 * 60 + 6.25 * 160 - 5 * age - 161
    
    multipliers = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725, "very active": 1.9}
    age_adj = 1.0
    if age < 18: age_adj = 1.2
    elif age < 25: age_adj = 1.1
    elif age < 45: age_adj = 1.0
    elif age < 60: age_adj = 0.95
    else: age_adj = 0.9
    
    calories = bmr * multipliers[activity_level] * age_adj
    return int(round(calories / 50) * 50)

def calculate_protein_target(age, gender, calories):
    if age < 18: protein_per_kg = 1.2
    elif age < 30: protein_per_kg = 1.0
    elif age < 50: protein_per_kg = 0.9
    else: protein_per_kg = 1.0
    
    weight_kg = 70 if gender == "Male" else 60
    return int(weight_kg * protein_per_kg)

def get_meal_suggestions(meal_time, diet_preference):
    suggestions = {
        "Non-Vegetarian": {
            "Breakfast": ["🍳 Anda bhurji with pav (280 cal)", "🥚 Boiled eggs with toast (220 cal)", "🍗 Chicken sandwich (350 cal)"],
            "Lunch": ["🍚 Chicken biryani with raita (450 cal)", "🥘 Fish curry with rice (400 cal)", "🍗 Chicken curry with roti (380 cal)"],
            "Dinner": ["🐟 Fish fry with dal and rice (420 cal)", "🍗 Chicken tikka masala with naan (480 cal)", "🥘 Mutton curry with rice (500 cal)"]
        },
        "Eggetarian": {
            "Breakfast": ["🍳 Masala omelette with bread (320 cal)", "🥚 Egg poha (250 cal)", "🧀 Cheese toast with tea (280 cal)"],
            "Lunch": ["🥚 Egg curry with rice (420 cal)", "🧀 Paneer bhurji with roti (380 cal)", "🍛 Egg biryani (400 cal)"],
            "Dinner": ["🧀 Paneer tikka with roti (380 cal)", "🥚 Egg fried rice (450 cal)", "🍛 Dal makhani with naan (420 cal)"]
        },
        "Vegetarian": {
            "Breakfast": ["🥣 Poha with peanuts (280 cal)", "🧀 Aloo paratha with curd (350 cal)", "🥛 Besan chilla with chutney (250 cal)"],
            "Lunch": ["🧀 Paneer butter masala with roti (480 cal)", "🥗 Rajma chawal (450 cal)", "🍛 Chole bhature (500 cal)"],
            "Dinner": ["🧀 Palak paneer with roti (380 cal)", "🥘 Mixed vegetable curry with rice (350 cal)", "🍛 Sambar rice with papad (320 cal)"]
        }
    }
    
    return suggestions.get(diet_preference, suggestions["Vegetarian"]).get(meal_time, [])

def save_food_to_session(food_data):
    try:
        food_data['timestamp'] = datetime.now().isoformat()
        food_data['time'] = datetime.now().strftime("%H:%M")
        food_data['date'] = datetime.now().strftime("%Y-%m-%d")
        
        if 'food_logs' not in st.session_state:
            st.session_state.food_logs = []
        
        st.session_state.food_logs.append(food_data)
        
        st.session_state.daily_totals['calories'] += food_data.get('calories', 0)
        st.session_state.daily_totals['protein'] += food_data.get('protein', 0)
        st.session_state.daily_totals['carbs'] += food_data.get('carbs', 0)
        st.session_state.daily_totals['fats'] += food_data.get('fats', 0)
        
        st.session_state.show_success = True
        st.session_state.success_message = f"✅ {food_data.get('food_name', 'Food')} saved!"
        
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def save_exercise_to_session(exercise_data):
    try:
        if 'exercise_logs' not in st.session_state:
            st.session_state.exercise_logs = []
        
        st.session_state.exercise_logs.append(exercise_data)
        st.session_state.daily_totals['calories_burned'] += exercise_data.get('calories_burned', 0)
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# ========== REACT-STYLE PAGES ==========
def render_landing_page():
    """React Landing Page"""
    st.markdown('<h1 class="modern-header">NutriMind</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: var(--text-light); font-size: 1.2rem; margin-bottom: 40px;">Scan • Track • Grow</p>', unsafe_allow_html=True)
    
    # Features Grid
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="modern-card" style="text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 16px;">📸</div>
            <h3>AI Food Scanner</h3>
            <p style="color: var(--text-light);">Upload food photos for instant nutrition analysis</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="modern-card" style="text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 16px;">📊</div>
            <h3>Smart Tracking</h3>
            <p style="color: var(--text-light);">Track your food intake and exercise with detailed analytics</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="modern-card" style="text-align: center;">
            <div style="font-size: 3rem; margin-bottom: 16px;">🥗</div>
            <h3>Personalized Recommendations</h3>
            <p style="color: var(--text-light);">Get meal suggestions based on your diet preference</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Get Started", use_container_width=True, type="primary"):
            st.session_state.page = "dashboard"
            st.rerun()
        
        if st.button("👤 Demo Mode", use_container_width=True, type="secondary"):
            st.session_state.user = {
                'name': "Demo User",
                'age': 25,
                'gender': "Male",
                'activity_level': "moderate",
                'joined': datetime.now().strftime("%Y-%m-%d")
            }
            st.session_state.goals = {
                'calories': 2000,
                'protein': 50,
                'carbs': 250,
                'fats': 65,
                'exercise_minutes': 30
            }
            st.session_state.page = "dashboard"
            st.rerun()

def render_dashboard():
    """React Dashboard Page"""
    if st.session_state.user is None:
        st.warning("Please create a profile first")
        render_landing_page()
        return
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"# 👋 Welcome back, {st.session_state.user['name']}!")
        st.markdown(f"*Today is {datetime.now().strftime('%A, %B %d')}*")
    
    with col2:
        if st.button("👤 Profile", use_container_width=True):
            st.session_state.page = "profile"
            st.rerun()
    
    # Success Message
    if st.session_state.show_success:
        st.markdown(f'<div class="success-toast">{st.session_state.success_message}</div>', unsafe_allow_html=True)
        st.session_state.show_success = False
    
    # Quick Stats
    st.markdown("## 📊 Today's Summary")
    
    row1 = st.columns(3)
    with row1[0]:
        calories_percent = min(100, (st.session_state.daily_totals['calories'] / st.session_state.goals['calories']) * 100)
        st.metric("🔥 Calories", f"{st.session_state.daily_totals['calories']}", f"{calories_percent:.0f}% of goal")
    
    with row1[1]:
        protein_percent = min(100, (st.session_state.daily_totals['protein'] / st.session_state.goals['protein']) * 100)
        st.metric("💪 Protein", f"{st.session_state.daily_totals['protein']}g", f"{protein_percent:.0f}% of goal")
    
    with row1[2]:
        exercise_percent = min(100, (len(st.session_state.exercise_logs) * 30 / st.session_state.goals['exercise_minutes']) * 100)
        st.metric("🏃 Exercise", f"{len(st.session_state.exercise_logs)} sessions", f"{exercise_percent:.0f}% of goal")
    
    # Quick Actions
    st.markdown("## ⚡ Quick Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📸 Log Food", use_container_width=True, type="primary"):
            st.session_state.page = "log_food"
            st.rerun()
    
    with col2:
        if st.button("🏋️ Log Exercise", use_container_width=True, type="primary"):
            st.session_state.page = "exercise"
            st.rerun()
    
    # Recent Activity
    st.markdown("## 📝 Recent Activity")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🍽️ Recent Meals")
        if st.session_state.food_logs:
            for log in st.session_state.food_logs[-3:]:
                st.markdown(f"""
                <div class="modern-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{log.get('food_name', 'Food')}</strong><br>
                            <small>🔥 {log.get('calories', 0)} cal • 💪 {log.get('protein', 0)}g protein</small>
                        </div>
                        <small style="color: var(--text-light);">{log.get('time', '')}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No meals logged yet")
    
    with col2:
        st.markdown("### 🏃 Recent Exercise")
        if st.session_state.exercise_logs:
            for log in st.session_state.exercise_logs[-3:]:
                st.markdown(f"""
                <div class="modern-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong>{log.get('name', 'Exercise')}</strong><br>
                            <small>⏱️ {log.get('duration', 0)} min • 🔥 {log.get('calories_burned', 0)} cal</small>
                        </div>
                        <small style="color: var(--text-light);">{log.get('time', '')}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No exercise logged yet")

def render_log_food():
    """React Food Logging Page"""
    st.markdown("# 📸 Log Food")
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()
    
    # Scan Options
    option = st.radio("Choose method:", 
                     ["📷 Camera Scan", "🏷️ Label Scan", "📝 Manual Entry"],
                     horizontal=True)
    
    if option == "📷 Camera Scan":
        st.markdown("### Take a photo of your meal")
        uploaded_image = st.file_uploader("Upload food image", type=["jpg", "jpeg", "png"])
        
        if uploaded_image:
            image = Image.open(uploaded_image)
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(image, width=200)
            
            with col2:
                if st.button("🔍 Analyze with AI", use_container_width=True):
                    nutrition = analyze_food_with_gemini("", image)
                    st.session_state.current_analyzed_food = nutrition
                    
                    # Show results
                    st.markdown(f"### {nutrition['food_name']}")
                    cols = st.columns(4)
                    with cols[0]:
                        st.metric("Calories", nutrition['calories'])
                    with cols[1]:
                        st.metric("Protein", f"{nutrition['protein']}g")
                    with cols[2]:
                        st.metric("Carbs", f"{nutrition['carbs']}g")
                    with cols[3]:
                        st.metric("Fats", f"{nutrition['fats']}g")
    
    elif option == "🏷️ Label Scan":
        st.markdown("### Upload food label")
        uploaded_label = st.file_uploader("Upload label image", type=["jpg", "jpeg", "png"], key="label")
        
        if uploaded_label and st.button("📊 Extract Nutrition Facts", use_container_width=True):
            with st.spinner("Analyzing label..."):
                time.sleep(1)
                nutrition = get_fallback_nutrition("nutrition label")
                st.session_state.current_analyzed_food = nutrition
                
                st.markdown(f"### {nutrition['food_name']}")
                cols = st.columns(4)
                with cols[0]:
                    st.metric("Calories", nutrition['calories'])
                with cols[1]:
                    st.metric("Protein", f"{nutrition['protein']}g")
                with cols[2]:
                    st.metric("Carbs", f"{nutrition['carbs']}g")
                with cols[3]:
                    st.metric("Fats", f"{nutrition['fats']}g")
    
    else:  # Manual Entry
        st.markdown("### Enter food details")
        food_input = st.text_input("Food name", placeholder="e.g., Masala Dosa, Apple, Pizza...")
        
        # Quick log buttons
        st.markdown("**Quick log common foods:**")
        cols = st.columns(4)
        quick_foods = ["Banana", "Apple", "Egg", "Rice"]
        for idx, food in enumerate(quick_foods):
            with cols[idx]:
                if st.button(f"🍎 {food}", use_container_width=True):
                    nutrition = get_fallback_nutrition(food.lower())
                    if save_food_to_session(nutrition):
                        st.session_state.page = "dashboard"
                        st.rerun()
        
        if food_input and st.button("🔍 Analyze with AI", use_container_width=True):
            nutrition = analyze_food_with_gemini(food_input)
            st.session_state.current_analyzed_food = nutrition
            
            st.markdown(f"### {nutrition['food_name']}")
            cols = st.columns(4)
            with cols[0]:
                st.metric("Calories", nutrition['calories'])
            with cols[1]:
                st.metric("Protein", f"{nutrition['protein']}g")
            with cols[2]:
                st.metric("Carbs", f"{nutrition['carbs']}g")
            with cols[3]:
                st.metric("Fats", f"{nutrition['fats']}g")
    
    # Save Section
    if st.session_state.current_analyzed_food:
        st.markdown("---")
        st.markdown("### Save Food")
        
        portion = st.select_slider("Portion size:", ["Small", "Medium", "Large"], value="Medium")
        multiplier = {"Small": 0.7, "Medium": 1.0, "Large": 1.5}
        
        nutrition = st.session_state.current_analyzed_food.copy()
        for key in ['calories', 'protein', 'carbs', 'fats']:
            nutrition[key] = int(nutrition[key] * multiplier[portion])
        
        if st.button("💾 Save to Log", use_container_width=True, type="primary"):
            if save_food_to_session(nutrition):
                st.session_state.current_analyzed_food = None
                st.session_state.page = "dashboard"
                st.rerun()

def render_exercise():
    """React Exercise Page"""
    st.markdown("# 🏋️ Exercise Tracker")
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()
    
    if st.session_state.daily_totals['calories'] > 0:
        st.info(f"Today's calories: **{st.session_state.daily_totals['calories']}**")
        
        # Exercise Suggestions
        st.markdown("### 💡 Exercise Suggestions")
        exercises = get_exercise_suggestions(st.session_state.daily_totals['calories'])
        
        for ex in exercises:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{ex['name']}**")
            with col2:
                st.write(f"{ex['duration']} min")
            with col3:
                if st.button("✅ Log", key=f"log_{ex['name']}"):
                    exercise_data = {
                        "name": ex['name'],
                        "duration": ex['duration'],
                        "calories_burned": ex['duration'] * ex['calories_per_min'],
                        "time": datetime.now().strftime("%H:%M"),
                        "date": datetime.now().strftime("%Y-%m-%d")
                    }
                    if save_exercise_to_session(exercise_data):
                        st.success("Exercise logged!")
                        time.sleep(1)
                        st.rerun()
    
    # Custom Exercise
    st.markdown("---")
    st.markdown("### 🎯 Custom Exercise")
    
    col1, col2 = st.columns(2)
    with col1:
        exercise_type = st.selectbox("Type", ["Running", "Walking", "Cycling", "Gym", "Yoga", "Swimming"])
        duration = st.slider("Duration (min)", 5, 180, 30)
    
    with col2:
        intensity = st.select_slider("Intensity", ["Light", "Moderate", "High", "Very High"])
        intensity_mult = {"Light": 5, "Moderate": 8, "High": 12, "Very High": 15}
        calories = duration * intensity_mult[intensity]
        st.metric("Calories Burned", calories)
    
    if st.button("💾 Log Custom Exercise", use_container_width=True, type="primary"):
        exercise_data = {
            "name": exercise_type,
            "duration": duration,
            "intensity": intensity,
            "calories_burned": calories,
            "time": datetime.now().strftime("%H:%M"),
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        if save_exercise_to_session(exercise_data):
            st.success("Exercise logged!")
            time.sleep(1)
            st.rerun()

def render_recommendations():
    """React Recommendations Page"""
    st.markdown("# 🥗 Meal Recommendations")
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()
    
    # Diet Preference
    st.markdown("### 🥗 Your Diet Preference")
    diet = st.radio("Select:", ["Vegetarian", "Non-Vegetarian", "Eggetarian"], 
                   horizontal=True, index=0)
    
    # Meal Time
    st.markdown("### 🕐 Meal Time")
    meal_time = st.radio("", ["Breakfast", "Lunch", "Dinner", "Snack"], horizontal=True)
    
    # Recommendations
    st.markdown(f"### 🍽️ {meal_time} Suggestions")
    suggestions = get_meal_suggestions(meal_time, diet)
    
    for i, suggestion in enumerate(suggestions):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"""
            <div class="modern-card">
                <strong>{suggestion}</strong><br>
                <small style="color: var(--text-light);">Perfect for your {diet} diet</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button(f"Add #{i+1}", key=f"add_{i}"):
                # Parse calories from suggestion
                import re
                cal_match = re.search(r'\((\d+)', suggestion)
                calories = int(cal_match.group(1)) if cal_match else 300
                protein = int(calories * 0.15)
                
                food_data = {
                    "food_name": suggestion.split(" (")[0],
                    "calories": calories,
                    "protein": protein,
                    "carbs": int(calories * 0.5),
                    "fats": int(calories * 0.25),
                    "insight": f"Recommended {meal_time}"
                }
                
                if save_food_to_session(food_data):
                    st.success("Meal added to log!")
                    time.sleep(1)
                    st.rerun()

def render_profile():
    """React Profile Page"""
    st.markdown("# 👤 Profile")
    
    if st.button("← Back to Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()
    
    if st.session_state.user is None:
        st.info("Create your profile")
        
        with st.form("profile_form"):
            name = st.text_input("Your Name")
            age = st.number_input("Age", 1, 100, 25)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            activity = st.select_slider("Activity", 
                                       ["Sedentary", "Light", "Moderate", "Active", "Very Active"],
                                       value="Moderate")
            
            if st.form_submit_button("Create Profile", type="primary"):
                if name:
                    calorie_target = calculate_calorie_target(age, gender.lower(), activity.lower())
                    protein_target = calculate_protein_target(age, gender, calorie_target)
                    
                    st.session_state.user = {
                        'name': name,
                        'age': age,
                        'gender': gender,
                        'activity_level': activity.lower()
                    }
                    
                    st.session_state.goals = {
                        'calories': calorie_target,
                        'protein': protein_target,
                        'carbs': int(calorie_target * 0.5 / 4),
                        'fats': int(calorie_target * 0.25 / 9),
                        'exercise_minutes': 30
                    }
                    
                    st.success(f"Welcome {name}!")
                    time.sleep(1)
                    st.rerun()
    
    else:
        # User Info
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Your Info")
            st.write(f"**Name:** {st.session_state.user['name']}")
            st.write(f"**Age:** {st.session_state.user['age']}")
            st.write(f"**Gender:** {st.session_state.user['gender']}")
            st.write(f"**Activity:** {st.session_state.user['activity_level'].title()}")
        
        with col2:
            st.markdown("### Daily Goals")
            for key, value in st.session_state.goals.items():
                st.write(f"**{key.title()}:** {value}")
        
        # Water Intake
        st.markdown("---")
        st.markdown("### 💧 Water Intake")
        water_cols = st.columns([2, 1, 1])
        with water_cols[0]:
            water = st.slider("Today's water (ml)", 0, 4000, st.session_state.daily_totals.get('water', 0), 250)
        
        with water_cols[1]:
            if st.button("Update"):
                st.session_state.daily_totals['water'] = water
                st.success("Water updated!")
                time.sleep(0.5)
                st.rerun()
        
        with water_cols[2]:
            if st.button("Logout", type="secondary"):
                st.session_state.user = None
                st.session_state.food_logs = []
                st.session_state.exercise_logs = []
                st.session_state.daily_totals = {k: 0 for k in st.session_state.daily_totals}
                st.session_state.page = "landing"
                st.rerun()

# ========== SIDEBAR NAVIGATION (React-style) ==========
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <div style="font-size: 2rem; margin-bottom: 10px;">🥗</div>
        <h2 style="margin: 0;">NutriMind</h2>
        <p style="color: var(--text-light); margin: 5px 0 20px;">Scan • Track • Grow</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    pages = [
        ("📊 Dashboard", "dashboard"),
        ("📸 Log Food", "log_food"),
        ("🏋️ Exercise", "exercise"),
        ("🥗 Meals", "recommendations"),
        ("👤 Profile", "profile")
    ]
    
    for icon, page_key in pages:
        if st.button(icon, key=page_key, use_container_width=True,
                    type="primary" if st.session_state.page == page_key else "secondary"):
            st.session_state.page = page_key
            st.rerun()
    
    # User info if logged in
    if st.session_state.user:
        st.markdown("---")
        st.markdown(f"**👋 {st.session_state.user['name']}**")
        st.markdown(f"*Age: {st.session_state.user['age']}*")

# ========== MAIN APP ROUTER ==========
if st.session_state.page == "landing":
    render_landing_page()
elif st.session_state.page == "dashboard":
    render_dashboard()
elif st.session_state.page == "log_food":
    render_log_food()
elif st.session_state.page == "exercise":
    render_exercise()
elif st.session_state.page == "recommendations":
    render_recommendations()
elif st.session_state.page == "profile":
    render_profile()

# ========== FOOTER ==========
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: var(--text-light); padding: 20px;">
    <p><strong>NutriMind</strong> | Scan • Track • Grow 🥗🧠🏃💪</p>
    <p><strong>Built for Google TechSprint</strong> | Team euphoria</p>
</div>
""", unsafe_allow_html=True)
