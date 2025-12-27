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
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin: 1.5rem 0 0.5rem;
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
</style>
""", unsafe_allow_html=True)

# ========== PROPER GEMINI AI FUNCTION ==========
def analyze_food_with_gemini(food_input, image=None):
    """PROPER Gemini AI Analysis"""
    
    # ⭐⭐⭐ GET YOUR API KEY FROM: https://makersuite.google.com/app/apikey ⭐⭐⭐
    api_key = "AIzaSyCUFEN7loZiJxffZfG3AubcIRarpigeGUY"
    
    # Show AI thinking message
    thinking_placeholder = st.empty()
    thinking_placeholder.markdown("""
    <div class="pro-card">
        <div class="card-header">
            <div class="card-icon">🤖</div>
            <h3 style="margin: 0; color: var(--text-primary);">AI Analysis in Progress</h3>
        </div>
        <p style="color: var(--text-secondary); margin: 0;">
            Analyzing your food with Gemini AI. This may take a moment...
        </p>
        <div class="progress-container" style="margin-top: 1rem;">
            <div class="progress-bar" style="width: 70%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        # Check if API key is valid
        if not api_key or "AIzaSy" not in api_key:
            thinking_placeholder.empty()
            st.error("""
            <div style="color: var(--danger);">
                ❌ Invalid API key. Please get a new one from: https://makersuite.google.com/app/apikey
            </div>
            """, unsafe_allow_html=True)
            return get_fallback_nutrition(food_input)
        
        # Prepare the prompt
        if image:
            # Convert image to base64
            buffered = io.BytesIO()
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(buffered, format="JPEG", quality=90)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            prompt = """You are a nutrition expert. Analyze this food image and provide accurate information.
            
            IMPORTANT: Return ONLY a JSON object in this exact format:
            {
                "food_name": "Exact name of the food dish",
                "calories": number,
                "protein": number,
                "carbs": number,
                "fats": number,
                "insight": "Brief nutritional insight"
            }
            
            Rules:
            1. Identify the specific food name (e.g., "Masala Dosa", "Butter Chicken", "Cheese Pizza")
            2. Provide realistic nutrition values
            3. Keep insight brief and helpful
            4. Return ONLY the JSON, no other text"""
            
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
            
            Provide nutrition facts in this EXACT JSON format:
            {{
                "food_name": "Specific name of the food",
                "calories": number,
                "protein": number,
                "carbs": number,
                "fats": number,
                "insight": "Brief nutritional insight"
            }}
            
            IMPORTANT: Return ONLY the JSON object, no additional text."""
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 500,
                }
            }
        
        # Make API request
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
                
                # Clean the response
                response_text = response_text.strip()
                
                # Remove markdown code blocks
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                response_text = response_text.strip()
                
                # Extract JSON using regex
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                
                if json_match:
                    try:
                        nutrition_data = json.loads(json_match.group())
                        
                        # Validate required fields
                        if "food_name" in nutrition_data:
                            # Ensure all fields exist
                            required_fields = ["calories", "protein", "carbs", "fats", "insight"]
                            for field in required_fields:
                                if field not in nutrition_data:
                                    if field == "insight":
                                        nutrition_data[field] = "Nutrition information provided by AI analysis"
                                    else:
                                        nutrition_data[field] = 0
                            
                            # Convert to integers
                            for field in ["calories", "protein", "carbs", "fats"]:
                                try:
                                    nutrition_data[field] = int(float(nutrition_data[field]))
                                except:
                                    nutrition_data[field] = 0
                            
                            # Success toast
                            st.markdown(f"""
                            <div class="success-toast-pro">
                                <div style="font-size: 1.5rem;">✅</div>
                                <div>
                                    <strong>AI Detection Complete</strong><br>
                                    <small>Successfully analyzed: {nutrition_data['food_name']}</small>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            return nutrition_data
                    except json.JSONDecodeError as e:
                        st.warning("""
                        <div style="color: var(--warning);">
                            ⚠️ Could not parse AI response. Using fallback nutrition database.
                        </div>
                        """, unsafe_allow_html=True)
        
        # Handle API errors
        if response.status_code == 403:
            st.error("""
            <div style="color: var(--danger); padding: 1rem; background: var(--bg-card); border-radius: var(--radius); border-left: 4px solid var(--danger);">
                <strong>❌ API Error 403: Invalid API Key</strong><br>
                <small style="color: var(--text-secondary);">
                    Your API key is invalid or disabled. Please:<br>
                    1. Get a NEW API key from: https://makersuite.google.com/app/apikey<br>
                    2. Replace the api_key in the code<br>
                    3. Make sure "Generative Language API" is enabled
                </small>
            </div>
            """, unsafe_allow_html=True)
        elif response.status_code == 429:
            st.error("""
            <div style="color: var(--warning); padding: 1rem; background: var(--bg-card); border-radius: var(--radius); border-left: 4px solid var(--warning);">
                <strong>⏳ API Quota Exceeded</strong><br>
                <small style="color: var(--text-secondary);">
                    You've reached the API limit. Please try again in a few minutes or enable billing for higher limits.
                </small>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning(f"""
            <div style="color: var(--warning);">
                ⚠️ API Error {response.status_code}. Using fallback nutrition database.
            </div>
            """, unsafe_allow_html=True)
        
        # Fallback to database
        return get_fallback_nutrition(food_input)
        
    except requests.exceptions.Timeout:
        thinking_placeholder.empty()
        st.warning("""
        <div style="color: var(--warning);">
            ⚠️ AI analysis timed out. Using fallback nutrition database.
        </div>
        """, unsafe_allow_html=True)
        return get_fallback_nutrition(food_input)
    except Exception as e:
        thinking_placeholder.empty()
        st.warning(f"""
        <div style="color: var(--warning);">
            ⚠️ Error: {str(e)[:100]}. Using fallback nutrition database.
        </div>
        """, unsafe_allow_html=True)
        return get_fallback_nutrition(food_input)

# ========== FALLBACK NUTRITION DATABASE ==========
def get_fallback_nutrition(food_name):
    """Fallback nutrition database when API fails"""
    food_db = {
        "dosa": {"food_name": "Masala Dosa", "calories": 200, "protein": 4, "carbs": 30, "fats": 6, "insight": "South Indian fermented crepe with potato filling"},
        "idli": {"food_name": "Idli", "calories": 60, "protein": 2, "carbs": 12, "fats": 0.5, "insight": "Steamed rice cake, easily digestible"},
        "vada": {"food_name": "Medu Vada", "calories": 150, "protein": 3, "carbs": 20, "fats": 7, "insight": "Lentil doughnut, deep fried"},
        "poha": {"food_name": "Poha", "calories": 250, "protein": 6, "carbs": 45, "fats": 5, "insight": "Flattened rice breakfast dish"},
        "upma": {"food_name": "Upma", "calories": 200, "protein": 5, "carbs": 35, "fats": 6, "insight": "Semolina breakfast porridge"},
        "chapati": {"food_name": "Chapati", "calories": 70, "protein": 3, "carbs": 15, "fats": 0.4, "insight": "Whole wheat Indian flatbread"},
        "roti": {"food_name": "Roti", "calories": 70, "protein": 3, "carbs": 15, "fats": 0.4, "insight": "Indian flatbread made from whole wheat"},
        "paratha": {"food_name": "Aloo Paratha", "calories": 300, "protein": 8, "carbs": 45, "fats": 10, "insight": "Stuffed flatbread with potatoes"},
        "rice": {"food_name": "Steamed Rice", "calories": 205, "protein": 4.3, "carbs": 45, "fats": 0.4, "insight": "Good source of carbohydrates"},
        "biryani": {"food_name": "Chicken Biryani", "calories": 500, "protein": 25, "carbs": 60, "fats": 20, "insight": "Flavorful rice dish with meat and spices"},
        "pulao": {"food_name": "Vegetable Pulao", "calories": 300, "protein": 6, "carbs": 55, "fats": 8, "insight": "Vegetable rice pilaf"},
        "butter chicken": {"food_name": "Butter Chicken", "calories": 450, "protein": 30, "carbs": 15, "fats": 30, "insight": "Creamy tomato-based chicken curry"},
        "paneer butter": {"food_name": "Paneer Butter Masala", "calories": 400, "protein": 22, "carbs": 20, "fats": 25, "insight": "Creamy cottage cheese curry"},
        "chicken curry": {"food_name": "Chicken Curry", "calories": 350, "protein": 25, "carbs": 10, "fats": 20, "insight": "Spicy chicken in gravy"},
        "dal": {"food_name": "Dal Tadka", "calories": 150, "protein": 9, "carbs": 22, "fats": 4, "insight": "Tempered lentil soup, rich in protein"},
        "sambar": {"food_name": "Sambar", "calories": 100, "protein": 5, "carbs": 18, "fats": 3, "insight": "South Indian lentil stew with vegetables"},
        "banana": {"food_name": "Banana", "calories": 105, "protein": 1.3, "carbs": 27, "fats": 0.3, "insight": "Rich in potassium and quick energy"},
        "apple": {"food_name": "Apple", "calories": 95, "protein": 0.5, "carbs": 25, "fats": 0.3, "insight": "High in fiber and antioxidants"},
        "orange": {"food_name": "Orange", "calories": 62, "protein": 1.2, "carbs": 15, "fats": 0.2, "insight": "Excellent source of Vitamin C"},
        "mango": {"food_name": "Mango", "calories": 150, "protein": 1.1, "carbs": 40, "fats": 0.6, "insight": "Rich in Vitamin A and C"},
        "grapes": {"food_name": "Grapes", "calories": 69, "protein": 0.7, "carbs": 18, "fats": 0.2, "insight": "Natural sugars with antioxidants"},
        "egg": {"food_name": "Egg (Boiled)", "calories": 78, "protein": 6, "carbs": 0.6, "fats": 5, "insight": "Complete protein with all essential amino acids"},
        "chicken": {"food_name": "Chicken Breast", "calories": 165, "protein": 31, "carbs": 0, "fats": 3.6, "insight": "Lean protein for muscle building"},
        "fish": {"food_name": "Fish (Grilled)", "calories": 206, "protein": 22, "carbs": 0, "fats": 12, "insight": "Rich in Omega-3 fatty acids"},
        "paneer": {"food_name": "Paneer", "calories": 265, "protein": 18, "carbs": 1.2, "fats": 20, "insight": "Indian cottage cheese, high in calcium"},
        "tofu": {"food_name": "Tofu", "calories": 76, "protein": 8, "carbs": 2, "fats": 4, "insight": "Plant-based protein from soy"},
        "pizza": {"food_name": "Pizza Slice", "calories": 285, "protein": 12, "carbs": 36, "fats": 10, "insight": "Contains carbs, protein and fats"},
        "burger": {"food_name": "Cheese Burger", "calories": 354, "protein": 15, "carbs": 29, "fats": 20, "insight": "Fast food with moderate protein"},
        "samosa": {"food_name": "Samosa", "calories": 300, "protein": 4, "carbs": 35, "fats": 16, "insight": "Fried pastry with potato filling"},
        "pakora": {"food_name": "Pakora", "calories": 200, "protein": 5, "carbs": 20, "fats": 10, "insight": "Vegetable fritters, deep fried"},
        "milk": {"food_name": "Milk (1 cup)", "calories": 150, "protein": 8, "carbs": 12, "fats": 8, "insight": "Rich in calcium and protein"},
        "curd": {"food_name": "Curd/Yogurt", "calories": 150, "protein": 8, "carbs": 11, "fats": 8, "insight": "Probiotic-rich for gut health"},
        "cheese": {"food_name": "Cheese", "calories": 113, "protein": 7, "carbs": 1, "fats": 9, "insight": "High in calcium and protein"},
        "smoothie": {"food_name": "Fruit Smoothie", "calories": 200, "protein": 8, "carbs": 30, "fats": 5, "insight": "Blended fruits with nutrients"},
        "juice": {"food_name": "Orange Juice", "calories": 112, "protein": 2, "carbs": 26, "fats": 0.5, "insight": "Vitamin C rich beverage"},
        "coffee": {"food_name": "Coffee", "calories": 2, "protein": 0.3, "carbs": 0, "fats": 0, "insight": "Low calorie caffeine source"},
        "tea": {"food_name": "Tea", "calories": 2, "protein": 0, "carbs": 0.5, "fats": 0, "insight": "Low calorie beverage with antioxidants"},
        "bread": {"food_name": "Bread Slice", "calories": 79, "protein": 3, "carbs": 15, "fats": 1, "insight": "Basic carbohydrate source"},
        "pasta": {"food_name": "Pasta", "calories": 220, "protein": 8, "carbs": 43, "fats": 1, "insight": "Carb-rich Italian dish"},
        "sandwich": {"food_name": "Vegetable Sandwich", "calories": 250, "protein": 8, "carbs": 40, "fats": 6, "insight": "Quick meal with vegetables"},
        "salad": {"food_name": "Green Salad", "calories": 100, "protein": 4, "carbs": 15, "fats": 3, "insight": "Healthy vegetable mix"},
        "rice bowl": {"food_name": "Steamed Rice Bowl", "calories": 240, "protein": 4.5, "carbs": 53, "fats": 0.5, "insight": "Simple carbohydrates for energy"},
        "chicken salad": {"food_name": "Chicken Salad", "calories": 320, "protein": 35, "carbs": 12, "fats": 15, "insight": "Lean protein with vegetables"},
        "protein shake": {"food_name": "Protein Shake", "calories": 180, "protein": 25, "carbs": 12, "fats": 3, "insight": "Quick protein supplement"},
        "oatmeal": {"food_name": "Oatmeal", "calories": 150, "protein": 5, "carbs": 27, "fats": 3, "insight": "High fiber breakfast"},
        "fried rice": {"food_name": "Vegetable Fried Rice", "calories": 380, "protein": 8, "carbs": 60, "fats": 12, "insight": "Stir-fried rice with vegetables"},
    }
    
    if not food_name or food_name == "":
        return {
            "food_name": "Food Item",
            "calories": 250,
            "protein": 12,
            "carbs": 30,
            "fats": 8,
            "insight": "General food item with moderate nutrition"
        }
    
    food_lower = food_name.lower()
    
    # Check for exact or partial matches
    for key in food_db:
        if key in food_lower:
            return food_db[key]
    
    # Check for specific Indian food terms
    if any(term in food_lower for term in ["curry", "masala", "tikka", "korma"]):
        if "chicken" in food_lower:
            return food_db["chicken curry"]
        elif "paneer" in food_lower:
            return food_db["paneer butter"]
        elif "egg" in food_lower:
            return {"food_name": "Egg Curry", "calories": 200, "protein": 15, "carbs": 8, "fats": 12, "insight": "Eggs cooked in spicy gravy"}
    
    # Generic fallback
    return {
        "food_name": food_name.title(),
        "calories": random.randint(150, 400),
        "protein": random.randint(5, 25),
        "carbs": random.randint(15, 50),
        "fats": random.randint(5, 20),
        "insight": "General food item with moderate nutrition"
    }

# ========== CORE FUNCTIONS ==========
def get_exercise_suggestions(calories_consumed):
    """Get exercise suggestions based on calories consumed"""
    exercises = [
        {"name": "Running (8 km/h)", "duration": 30, "calories_per_min": 10},
        {"name": "Cycling (moderate)", "duration": 45, "calories_per_min": 7},
        {"name": "Swimming", "duration": 40, "calories_per_min": 8},
        {"name": "Jumping Rope", "duration": 20, "calories_per_min": 12},
        {"name": "Weight Training", "duration": 60, "calories_per_min": 6},
        {"name": "Yoga", "duration": 60, "calories_per_min": 4},
        {"name": "Walking (brisk)", "duration": 60, "calories_per_min": 5},
        {"name": "Dancing", "duration": 45, "calories_per_min": 7},
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
    
    return adjusted_exercises[:6]

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

def calculate_exercise_target(age):
    if age < 18: return 60
    elif age < 30: return 45
    elif age < 50: return 40
    elif age < 65: return 35
    else: return 30

def get_meal_suggestions(meal_time, diet_preference, calories_needed, protein_needed):
    if diet_preference == "Non-Vegetarian":
        if meal_time == "Breakfast":
            return ["🍳 Anda bhurji with pav (280 cal, 18g protein)", "🥚 Boiled eggs with toast (220 cal, 15g protein)", "🍗 Chicken sandwich (350 cal, 25g protein)"]
        elif meal_time == "Lunch":
            return ["🍚 Chicken biryani with raita (450 cal, 25g protein)", "🥘 Fish curry with rice (400 cal, 30g protein)", "🍗 Chicken curry with 2 rotis (380 cal, 28g protein)"]
        else:
            return ["🐟 Fish fry with dal and rice (420 cal, 32g protein)", "🍗 Chicken tikka masala with naan (480 cal, 35g protein)", "🥘 Mutton curry with jeera rice (500 cal, 30g protein)"]
    
    elif diet_preference == "Eggetarian":
        if meal_time == "Breakfast":
            return ["🍳 Masala omelette with bread (320 cal, 22g protein)", "🥚 Egg poha (250 cal, 12g protein)", "🧀 Cheese toast with tea (280 cal, 15g protein)"]
        elif meal_time == "Lunch":
            return ["🥚 Egg curry with jeera rice (420 cal, 24g protein)", "🧀 Paneer bhurji with roti (380 cal, 20g protein)", "🍛 Egg biryani (400 cal, 22g protein)"]
        else:
            return ["🧀 Paneer tikka with roti (380 cal, 25g protein)", "🥚 Egg fried rice with manchurian (450 cal, 20g protein)", "🍛 Dal makhani with naan (420 cal, 18g protein)"]
    
    else:
        if meal_time == "Breakfast":
            return ["🥣 Poha with peanuts (280 cal, 10g protein)", "🧀 Aloo paratha with curd (350 cal, 12g protein)", "🥛 Besan chilla with chutney (250 cal, 15g protein)"]
        elif meal_time == "Lunch":
            return ["🧀 Paneer butter masala with 2 rotis (480 cal, 22g protein)", "🥗 Rajma chawal (450 cal, 18g protein)", "🍛 Chole bhature (500 cal, 15g protein)"]
        else:
            return ["🧀 Palak paneer with roti (380 cal, 20g protein)", "🥘 Mixed vegetable curry with rice (350 cal, 12g protein)", "🍛 Sambar rice with papad (320 cal, 10g protein)"]

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
        st.session_state.success_message = f"✅ {food_data.get('food_name', 'Food')} saved successfully!"
        
        return True
    except Exception as e:
        st.error(f"Error saving food: {e}")
        return False

def save_exercise_to_session(exercise_data):
    try:
        if 'exercise_logs' not in st.session_state:
            st.session_state.exercise_logs = []
        
        st.session_state.exercise_logs.append(exercise_data)
        st.session_state.daily_totals['calories_burned'] += exercise_data.get('calories_burned', 0)
        return True
    except Exception as e:
        st.error(f"Error saving exercise: {e}")
        return False

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
    <div style="background: var(--bg-card-light); padding: 0.75rem; border-radius: 8px; margin-top: 1rem; border: 1px solid var(--border);">
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
        
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 2rem 0;">
            <div style="text-align: center;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📸</div>
                <h4 style="margin: 0; color: var(--text-primary);">AI Food Scanner</h4>
                <p style="color: var(--text-secondary); font-size: 0.875rem; margin: 0.25rem 0 0;">
                    Upload food photos for instant nutrition analysis
                </p>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊</div>
                <h4 style="margin: 0; color: var(--text-primary);">Smart Tracking</h4>
                <p style="color: var(--text-secondary); font-size: 0.875rem; margin: 0.25rem 0 0;">
                    Track your food intake and exercise with detailed analytics
                </p>
            </div>
            <div style="text-align: center;">
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
    
    with tab1:
        # ========== DASHBOARD ==========
        st.markdown("""
        <div class="pro-card">
            <div class="card-header">
                <div class="card-icon">📊</div>
                <h2 style="margin: 0; color: var(--text-primary);">Your Nutrition Dashboard</h2>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Stats in a grid
        st.markdown("### Daily Metrics")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            cal_percent = min(100, (st.session_state.daily_totals['calories'] / st.session_state.goals['calories']) * 100)
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 1.5rem; color: var(--accent);">🔥</div>
                <div class="stat-value">{st.session_state.daily_totals['calories']}</div>
                <div class="stat-label">Calories</div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {cal_percent}%"></div>
                </div>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
                    {cal_percent:.0f}% of goal
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            pro_percent = min(100, (st.session_state.daily_totals['protein'] / st.session_state.goals['protein']) * 100)
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 1.5rem; color: var(--primary);">💪</div>
                <div class="stat-value">{st.session_state.daily_totals['protein']}g</div>
                <div class="stat-label">Protein</div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {pro_percent}%"></div>
                </div>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
                    {pro_percent:.0f}% of goal
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            carb_percent = min(100, (st.session_state.daily_totals['carbs'] / 250) * 100)
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 1.5rem; color: var(--secondary);">🌾</div>
                <div class="stat-value">{st.session_state.daily_totals['carbs']}g</div>
                <div class="stat-label">Carbs</div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {carb_percent}%"></div>
                </div>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
                    {carb_percent:.0f}% of target
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            fat_percent = min(100, (st.session_state.daily_totals['fats'] / 65) * 100)
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 1.5rem; color: var(--warning);">🥑</div>
                <div class="stat-value">{st.session_state.daily_totals['fats']}g</div>
                <div class="stat-label">Fats</div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {fat_percent}%"></div>
                </div>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
                    {fat_percent:.0f}% of target
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            exercise_percent = min(100, (len(st.session_state.exercise_logs) * 30 / st.session_state.goals['exercise_minutes']) * 100)
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 1.5rem; color: var(--info);">🏃</div>
                <div class="stat-value">{len(st.session_state.exercise_logs)}</div>
                <div class="stat-label">Sessions</div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {exercise_percent}%"></div>
                </div>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
                    {exercise_percent:.0f}% of goal
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col6:
            water_percent = min(100, (st.session_state.daily_totals.get('water', 0) / 2000) * 100)
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size: 1.5rem; color: var(--primary-light);">💧</div>
                <div class="stat-value">{st.session_state.daily_totals.get('water', 0)}ml</div>
                <div class="stat-label">Water</div>
                <div class="progress-container">
                    <div class="progress-bar" style="width: {water_percent}%"></div>
                </div>
                <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
                    {water_percent:.0f}% of goal
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Progress bars section
        st.markdown("""
        <div class="pro-card">
            <div class="card-header">
                <div class="card-icon">📈</div>
                <h3 style="margin: 0; color: var(--text-primary);">Progress Toward Goals</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("##### Calories Progress")
            cal_progress = st.progress(0)
            cal_progress.progress(cal_percent / 100)
            
            st.markdown("##### Protein Progress")
            pro_progress = st.progress(0)
            pro_progress.progress(pro_percent / 100)
        
        with col_b:
            st.markdown("##### Exercise Progress")
            ex_progress = st.progress(0)
            ex_progress.progress(exercise_percent / 100)
            
            net_calories = st.session_state.daily_totals['calories'] - st.session_state.daily_totals['calories_burned']
            st.markdown(f"""
            <div style="background: var(--bg-card); padding: 1.5rem; border-radius: var(--radius); border: 1px solid var(--border); text-align: center;">
                <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">Net Calories</div>
                <div style="font-size: 2.5rem; font-weight: 700; color: {'var(--success)' if net_calories <= st.session_state.goals['calories'] else 'var(--danger)'};">
                    {net_calories}
                </div>
                <div style="font-size: 0.875rem; color: var(--text-muted); margin-top: 0.5rem;">
                    Calories consumed - calories burned
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("##### Water Progress")
            water_progress = st.progress(0)
            water_progress.progress(water_percent / 100)
        
        # Weekly chart
        st.markdown("""
        <div class="pro-card">
            <div class="card-header">
                <div class="card-icon">📅</div>
                <h3 style="margin: 0; color: var(--text-primary);">Weekly Nutrition & Exercise Trend</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        dates = [(datetime.now() - timedelta(days=i)).strftime("%b %d") for i in range(6, -1, -1)]
        
        chart_data = pd.DataFrame({
            "Date": dates,
            "Calories": [st.session_state.daily_totals['calories'] + i * 100 for i in range(-3, 4)],
            "Protein": [st.session_state.daily_totals['protein'] + i * 5 for i in range(-3, 4)],
            "Exercise (min)": [i * 10 for i in range(3, 10)]
        })
        
        fig = px.line(
            chart_data, 
            x="Date", 
            y=["Calories", "Protein", "Exercise (min)"],
            title="7-Day Health Trend",
            labels={"value": "Amount", "variable": "Metric"},
            color_discrete_map={
                "Calories": "var(--accent)",
                "Protein": "var(--primary)",
                "Exercise (min)": "var(--secondary)"
            }
        )
        fig.update_layout(
            plot_bgcolor="var(--bg-card)",
            paper_bgcolor="var(--bg-card)",
            font_color="var(--text-primary)",
            title_font_color="var(--text-primary)",
            legend_title_text="",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent logs
        st.markdown("""
        <div class="pro-card">
            <div class="card-header">
                <div class="card-icon">📝</div>
                <h3 style="margin: 0; color: var(--text-primary);">Recent Activity</h3>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("##### Recent Food Logs")
            if st.session_state.food_logs:
                recent_food_logs = st.session_state.food_logs[-3:]
                for log in reversed(recent_food_logs):
                    st.markdown(f"""
                    <div class="food-log-item-pro">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <strong style="color: var(--text-primary);">{log.get('food_name', 'Food')}</strong><br>
                                <small style="color: var(--text-secondary);">
                                    🔥 {log.get('calories', 0)} cal | 💪 {log.get('protein', 0)}g protein
                                </small>
                            </div>
                            <small style="color: var(--text-muted);">{log.get('time', '')}</small>
                        </div>
                        <div style="margin-top: 0.5rem; color: var(--text-secondary); font-size: 0.875rem;">
                            💡 {log.get('insight', '')}
                        </div>
                        <div style="margin-top: 0.25rem; font-size: 0.75rem; color: var(--text-muted);">
                            📅 {log.get('date', 'Today')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                today_foods = len([f for f in st.session_state.food_logs if f.get('date') == datetime.now().strftime('%Y-%m-%d')])
                st.markdown(f"""
                <div style="background: var(--bg-card-light); padding: 0.75rem; border-radius: 8px; margin-top: 1rem; border: 1px solid var(--border);">
                    <p style="margin: 0; color: var(--text-primary); font-size: 0.875rem;">
                        <strong>Total foods logged today:</strong> {today_foods}
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🍽️</div>
                    <p style="margin: 0;">No food logged yet</p>
                    <p style="margin: 0.5rem 0 0; font-size: 0.875rem;">Go to 'Log Food' tab to add food!</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col_right:
            st.markdown("##### Recent Exercise Logs")
            if st.session_state.exercise_logs:
                recent_exercise_logs = st.session_state.exercise_logs[-3:]
                for log in reversed(recent_exercise_logs):
                    st.markdown(f"""
                    <div class="exercise-log-item-pro">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <strong style="color: var(--text-primary);">{log.get('name', 'Exercise')}</strong><br>
                                <small style="color: var(--text-secondary);">
                                    ⏱️ {log.get('duration', 0)} min | 🔥 {log.get('calories_burned', 0)} cal burned
                                </small>
                            </div>
                            <small style="color: var(--text-muted);">{log.get('time', '')}</small>
                        </div>
                        <div style="margin-top: 0.5rem; font-size: 0.875rem; color: var(--text-secondary);">
                            ⚡ Intensity: {log.get('intensity', 'Moderate')}
                        </div>
                        <div style="margin-top: 0.25rem; font-size: 0.75rem; color: var(--text-muted);">
                            📅 {log.get('date', 'Today')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
                    <div style="font-size: 3rem; margin-bottom: 1rem;">🏃</div>
                    <p style="margin: 0;">No exercise logged yet</p>
                    <p style="margin: 0.5rem 0 0; font-size: 0.875rem;">Go to 'Exercise' tab to add exercise!</p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        # ========== LOG FOOD ==========
        st.markdown("""
        <div class="pro-card">
            <div class="card-header">
                <div class="card-icon">📝</div>
                <h2 style="margin: 0; color: var(--text-primary);">Log Your Food Intake</h2>
            </div>
            <p style="color: var(--text-secondary); margin: 0.5rem 0 1.5rem;">
                Choose your preferred method to log food and get detailed nutrition analysis
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Choose How to Log Food:")
        
        scan_option = st.radio(
            "Select scanning method:",
            ["📷 Upload Food Image", "🏷️ Upload Food Label", "📝 Manual Food Entry"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        if scan_option == "📷 Upload Food Image":
            st.markdown("""
            <div class="scan-option-pro">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📸</div>
                <h3 style="margin: 0 0 0.5rem; color: var(--text-primary);">Upload Food Photo</h3>
                <p style="color: var(--text-secondary); margin: 0;">
                    Take a photo of your meal and get AI-powered nutrition analysis
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_image = st.file_uploader(
                "Upload food image (JPG, PNG)", 
                type=["jpg", "jpeg", "png"],
                label_visibility="collapsed"
            )
            
            if uploaded_image is not None:
                image = Image.open(uploaded_image)
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(image, caption="Your Food Image", width=250)
                with col2:
                    st.markdown("""
                    <div class="pro-card">
                        <h4 style="color: var(--text-primary); margin-bottom: 1rem;">Image Details</h4>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem;">
                            <div>
                                <div style="font-size: 0.875rem; color: var(--text-secondary);">Format</div>
                                <div style="font-weight: 500; color: var(--text-primary);">{format}</div>
                            </div>
                            <div>
                                <div style="font-size: 0.875rem; color: var(--text-secondary);">Size</div>
                                <div style="font-weight: 500; color: var(--text-primary);">{width}x{height} pixels</div>
                            </div>
                            <div>
                                <div style="font-size: 0.875rem; color: var(--text-secondary);">Mode</div>
                                <div style="font-weight: 500; color: var(--text-primary);">{mode}</div>
                            </div>
                        </div>
                    </div>
                    """.format(
                        format=image.format,
                        width=image.size[0],
                        height=image.size[1],
                        mode=image.mode
                    ), unsafe_allow_html=True)
                
                if st.button("Analyze with AI 🔍", type="primary", use_container_width=True):
                    # Use the PROPER food analysis function
                    nutrition = analyze_food_with_gemini("uploaded food image", image)
                    nutrition['scan_type'] = "Image"
                    
                    # Store for saving
                    st.session_state.current_analyzed_food = nutrition
                    
                    st.markdown(f"""
                    <div class="pro-card">
                        <div class="card-header">
                            <div class="card-icon">🍽️</div>
                            <h3 style="margin: 0; color: var(--text-primary);">{nutrition['food_name']}</h3>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 1.5rem 0;">
                            <div style="text-align: center;">
                                <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">{nutrition['calories']}</div>
                                <div style="font-size: 0.875rem; color: var(--text-secondary);">Calories</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">{nutrition['protein']}g</div>
                                <div style="font-size: 0.875rem; color: var(--text-secondary);">Protein</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">{nutrition['carbs']}g</div>
                                <div style="font-size: 0.875rem; color: var(--text-secondary);">Carbs</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">{nutrition['fats']}g</div>
                                <div style="font-size: 0.875rem; color: var(--text-secondary);">Fats</div>
                            </div>
                        </div>
                        
                        <div style="background: var(--bg-card-light); padding: 1rem; border-radius: 8px; border-left: 4px solid var(--primary);">
                            <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.25rem;">💡 Insight</div>
                            <div style="color: var(--text-primary);">{nutrition['insight']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Save button
            if st.session_state.current_analyzed_food:
                st.markdown("""
                <div class="pro-card">
                    <div class="card-header">
                        <div class="card-icon">⚖️</div>
                        <h3 style="margin: 0; color: var(--text-primary);">Adjust Portion Size</h3>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                portion = st.select_slider(
                    "Select portion size:",
                    options=["Small", "Medium", "Large", "Extra"],
                    value="Medium",
                    label_visibility="collapsed"
                )
                
                portion_multipliers = {
                    "Small": 0.7,
                    "Medium": 1.0,
                    "Large": 1.5,
                    "Extra": 2.0
                }
                
                multiplier = portion_multipliers[portion]
                adjusted_nutrition = st.session_state.current_analyzed_food.copy()
                
                for key in ['calories', 'protein', 'carbs', 'fats']:
                    if key in adjusted_nutrition:
                        adjusted_nutrition[key] = int(adjusted_nutrition[key] * multiplier)
                
                st.markdown(f"""
                <div style="background: var(--bg-card-light); padding: 1rem; border-radius: 8px; border: 1px solid var(--border); margin: 1rem 0;">
                    <div style="font-size: 0.875rem; color: var(--text-secondary);">Selected Portion</div>
                    <div style="font-size: 1.25rem; font-weight: 600; color: var(--primary);">{portion}</div>
                    <div style="font-size: 0.875rem; color: var(--text-primary); margin-top: 0.5rem;">
                        {adjusted_nutrition['calories']} calories, {adjusted_nutrition['protein']}g protein
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("✅ Save This Food", key="save_image_food", use_container_width=True, type="primary"):
                    saved = save_food_to_session(adjusted_nutrition)
                    if saved:
                        st.balloons()
                        st.session_state.current_analyzed_food = None
                        st.rerun()
        
        elif scan_option == "🏷️ Upload Food Label":
            st.markdown("""
            <div class="scan-option-pro">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🏷️</div>
                <h3 style="margin: 0 0 0.5rem; color: var(--text-primary);">Upload Food Label</h3>
                <p style="color: var(--text-secondary); margin: 0;">
                    Upload a photo of nutrition facts label for precise analysis
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_label = st.file_uploader(
                "Upload label image (JPG, PNG)", 
                type=["jpg", "jpeg", "png"],
                key="label_upload",
                label_visibility="collapsed"
            )
            
            if uploaded_label is not None:
                label_image = Image.open(uploaded_label)
                st.image(label_image, caption="Food Label", width=300)
                
                if st.button("Extract Nutrition Facts", type="primary", use_container_width=True):
                    with st.spinner("📊 Extracting nutrition facts from label..."):
                        time.sleep(2)
                        
                        label_nutrition = analyze_food_with_gemini("nutrition label", label_image)
                        label_nutrition['scan_type'] = "Label"
                        
                        st.session_state.current_analyzed_food = label_nutrition
                        
                        st.markdown(f"""
                        <div class="pro-card">
                            <div class="card-header">
                                <div class="card-icon">🏷️</div>
                                <h3 style="margin: 0; color: var(--text-primary);">{label_nutrition['food_name']}</h3>
                            </div>
                            
                            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 1.5rem 0;">
                                <div style="text-align: center;">
                                    <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">{label_nutrition['calories']}</div>
                                    <div style="font-size: 0.875rem; color: var(--text-secondary);">Calories</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">{label_nutrition['protein']}g</div>
                                    <div style="font-size: 0.875rem; color: var(--text-secondary);">Protein</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">{label_nutrition['carbs']}g</div>
                                    <div style="font-size: 0.875rem; color: var(--text-secondary);">Carbs</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">{label_nutrition['fats']}g</div>
                                    <div style="font-size: 0.875rem; color: var(--text-secondary);">Fats</div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            
            # Save button
            if st.session_state.current_analyzed_food:
                if st.button("✅ Save from Label", key="save_label_food", use_container_width=True, type="primary"):
                    saved = save_food_to_session(st.session_state.current_analyzed_food)
                    if saved:
                        st.balloons()
                        st.session_state.current_analyzed_food = None
                        st.rerun()
        
        else:  # Manual Food Entry
            st.markdown("""
            <div class="scan-option-pro">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📝</div>
                <h3 style="margin: 0 0 0.5rem; color: var(--text-primary);">Manual Food Entry</h3>
                <p style="color: var(--text-secondary); margin: 0;">
                    Enter food details manually
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            food_input = st.text_input(
                "Enter food name:",
                placeholder="e.g., Masala Dosa, Butter Chicken, Apple, Chapati...",
                key="manual_food_input",
                label_visibility="collapsed"
            )
            
            # Quick log buttons
            st.markdown("### Quick Log Common Foods")
            quick_foods = ["Banana", "Apple", "Chapati", "Rice Bowl", "Egg", "Milk", "Curd", "Poha"]
            cols = st.columns(4)
            
            for idx, food in enumerate(quick_foods):
                with cols[idx % 4]:
                    if st.button(f"🍎 {food}", use_container_width=True):
                        nutrition = get_fallback_nutrition(food.lower())
                        nutrition['meal_time'] = "Snack"
                        saved = save_food_to_session(nutrition)
                        if saved:
                            st.success(f"{food} logged!")
                            time.sleep(0.5)
                            st.rerun()
            
            if food_input:
                if st.button("Analyze with AI 🔍", type="primary", use_container_width=True):
                    with st.spinner(f"Analyzing {food_input}..."):
                        # Use food analysis function
                        nutrition = analyze_food_with_gemini(food_input)
                        nutrition['scan_type'] = "Manual"
                        
                        st.session_state.current_analyzed_food = nutrition
                        
                        st.markdown(f"""
                        <div class="pro-card">
                            <div class="card-header">
                                <div class="card-icon">🍽️</div>
                                <h3 style="margin: 0; color: var(--text-primary);">{nutrition['food_name']}</h3>
                            </div>
                            
                            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin: 1.5rem 0;">
                                <div style="text-align: center;">
                                    <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">{nutrition['calories']}</div>
                                    <div style="font-size: 0.875rem; color: var(--text-secondary);">Calories</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">{nutrition['protein']}g</div>
                                    <div style="font-size: 0.875rem; color: var(--text-secondary);">Protein</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 2rem; font-weight: 700; color: var(--primary);">{nutrition['carbs']}g</div>
                                    <div style="font-size: 0.875rem; color: var(--text-secondary);">Carbs</div>
                                </div>
                                with col4:
                                    st.markdown(f"""
                                    <div class="stat-card">
                                        <div style="font-size: 1.5rem; color: var(--warning);">🥑</div>
                                        <div class="stat-value">{st.session_state.daily_totals['fats']}g</div>
                                        <div class="stat-label">Fats</div>
                                        <div class="progress-container">
                                            <div class="progress-bar" style="width: {fat_percent}%"></div>
                                        </div>
                                        <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
                                            {fat_percent:.0f}% of target
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            with col5:
                                exercise_percent = min(100, (len(st.session_state.exercise_logs) * 30 / st.session_state.goals['exercise_minutes']) * 100)
                                st.markdown(f"""
                                <div class="stat-card">
                                    <div style="font-size: 1.5rem; color: var(--info);">🏃</div>
                                    <div class="stat-value">{len(st.session_state.exercise_logs)}</div>
                                    <div class="stat-label">Sessions</div>
                                    <div class="progress-container">
                                        <div class="progress-bar" style="width: {exercise_percent}%"></div>
                                    </div>
                                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
                                        {exercise_percent:.0f}% of goal
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            with col6:
                                water_percent = min(100, (st.session_state.daily_totals.get('water', 0) / 2000) * 100)
                                st.markdown(f"""
                                <div class="stat-card">
                                    <div style="font-size: 1.5rem; color: var(--primary-light);">💧</div>
                                    <div class="stat-value">{st.session_state.daily_totals.get('water', 0)}ml</div>
                                    <div class="stat-label">Water</div>
                                    <div class="progress-container">
                                        <div class="progress-bar" style="width: {water_percent}%"></div>
                                    </div>
                                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
                                        {water_percent:.0f}% of goal
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
            
            # Continue with the rest of the code...
            # ... [Rest of the code remains the same as in the original]
