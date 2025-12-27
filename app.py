# app.py - NutriMind with PROPER Gemini AI 2.5 Flash Lite
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

# Configure the page
st.set_page_config(
    page_title="NutriMind - AI Nutrition Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful green theme
st.markdown("""
<style>
    /* Beautiful Green Theme Variables */
    :root {
        --green-primary: #10B981;
        --green-secondary: #059669;
        --green-light: #34D399;
        --green-dark: #065F46;
        --green-accent: #10B981;
        --bg-dark: #0A1929;
        --bg-card: #1E293B;
        --text-primary: #F0FDF4;
        --text-secondary: #BBF7D0;
        --border-color: #047857;
        --gradient-start: #10B981;
        --gradient-end: #065F46;
    }
    
    /* Main Header with beautiful green gradient */
    .main-header {
        font-size: 3.5rem;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #34D399 0%, #10B981 25%, #059669 50%, #047857 75%, #065F46 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        letter-spacing: -0.5px;
        padding: 10px 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Slogan with green accent */
    .slogan {
        text-align: center;
        font-size: 1.3rem;
        color: #34D399;
        font-weight: 600;
        letter-spacing: 1.5px;
        margin: 5px 0 30px 0;
        text-transform: uppercase;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        opacity: 0.9;
    }
    
    /* Nutri Card - Modern glass morphism effect */
    .nutri-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.15) 100%);
        backdrop-filter: blur(10px);
        color: var(--text-primary);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(16, 185, 129, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .nutri-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(16, 185, 129, 0.3);
    }
    
    /* Scan option cards */
    .scan-option {
        text-align: center;
        padding: 25px;
        border: 2px dashed #34D399;
        border-radius: 15px;
        margin: 15px 0;
        transition: all 0.3s;
        background: rgba(5, 150, 105, 0.1);
        color: var(--text-primary);
        border-color: var(--green-light);
    }
    
    .scan-option:hover {
        background: rgba(5, 150, 105, 0.2);
        border-color: var(--green-primary);
        transform: scale(1.02);
    }
    
    /* Food log items */
    .food-log-item {
        background: linear-gradient(135deg, rgba(6, 95, 70, 0.8) 0%, rgba(4, 120, 87, 0.9) 100%);
        padding: 20px;
        border-radius: 12px;
        margin: 12px 0;
        border-left: 5px solid #10B981;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        color: var(--text-primary) !important;
        border: 1px solid rgba(16, 185, 129, 0.3);
        transition: transform 0.2s;
    }
    
    .food-log-item:hover {
        transform: translateX(5px);
        border-left: 5px solid #34D399;
    }
    
    /* Exercise log items */
    .exercise-log-item {
        background: linear-gradient(135deg, rgba(6, 95, 70, 0.8) 0%, rgba(4, 120, 87, 0.9) 100%);
        padding: 20px;
        border-radius: 12px;
        margin: 12px 0;
        border-left: 5px solid #059669;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        color: var(--text-primary) !important;
        border: 1px solid rgba(5, 150, 105, 0.3);
        transition: transform 0.2s;
    }
    
    .exercise-log-item:hover {
        transform: translateX(5px);
        border-left: 5px solid #10B981;
    }
    
    /* Success toast */
    .success-toast {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.9) 0%, rgba(5, 150, 105, 0.95) 100%);
        color: var(--text-primary);
        padding: 18px;
        border-radius: 12px;
        margin: 15px 0;
        animation: fadeIn 0.5s;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
        border: 1px solid rgba(52, 211, 153, 0.5);
        font-weight: 500;
        text-align: center;
    }
    
    /* AI thinking box */
    .ai-thinking {
        background: linear-gradient(135deg, rgba(6, 95, 70, 0.8) 0%, rgba(4, 120, 87, 0.9) 100%);
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        border-left: 5px solid #10B981;
        color: var(--text-primary);
        border: 1px solid rgba(16, 185, 129, 0.3);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { border-left-color: #10B981; }
        50% { border-left-color: #34D399; }
        100% { border-left-color: #10B981; }
    }
    
    /* Meal suggestion card */
    .meal-suggestion-card {
        padding: 20px;
        background: linear-gradient(135deg, rgba(6, 95, 70, 0.8) 0%, rgba(4, 120, 87, 0.9) 100%);
        border-radius: 12px;
        margin: 15px 0;
        border-left: 5px solid #10B981;
        border: 1px solid rgba(16, 185, 129, 0.3);
        transition: transform 0.3s;
    }
    
    .meal-suggestion-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3);
    }
    
    .meal-suggestion-card strong {
        color: #FFFFFF !important;
        font-size: 1.1em;
        font-weight: 600;
    }
    
    .meal-suggestion-card small {
        color: #BBF7D0 !important;
        opacity: 0.9;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #10B981, #34D399);
        border-radius: 4px;
    }
    
    /* Buttons - Beautiful green gradient */
    .stButton > button {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #34D399 0%, #10B981 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
        border: none;
    }
    
    .stButton > button[kind="secondary"] {
        background: rgba(16, 185, 129, 0.1);
        color: #10B981;
        border: 1px solid #10B981;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: rgba(16, 185, 129, 0.2);
        color: #34D399;
        border: 1px solid #34D399;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1lcbmhc {
        background-color: #0F172A;
        border-right: 1px solid rgba(16, 185, 129, 0.2);
    }
    
    /* Metric cards */
    .stMetric {
        background: linear-gradient(135deg, rgba(6, 95, 70, 0.8) 0%, rgba(4, 120, 87, 0.9) 100%);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(16, 185, 129, 0.3);
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    
    .stMetric label {
        color: #BBF7D0 !important;
        font-weight: 500;
    }
    
    .stMetric div {
        color: #FFFFFF !important;
        font-weight: 700;
        font-size: 1.4rem !important;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: rgba(6, 95, 70, 0.1);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    /* Selectbox */
    .stSelectbox > div > div > div {
        background: rgba(6, 95, 70, 0.1);
        border-color: rgba(16, 185, 129, 0.3);
        color: var(--text-primary);
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #10B981, #34D399);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background: rgba(6, 95, 70, 0.1);
        color: var(--text-primary);
        border-color: rgba(16, 185, 129, 0.3);
        border-radius: 8px;
    }
    
    /* File uploader */
    .stFileUploader > div > div {
        background: rgba(6, 95, 70, 0.1);
        border-color: rgba(16, 185, 129, 0.3);
        border-radius: 8px;
    }
    
    /* Info boxes */
    .stInfo {
        background: linear-gradient(135deg, rgba(6, 95, 70, 0.8) 0%, rgba(4, 120, 87, 0.9) 100%);
        border-left: 5px solid #10B981;
        color: var(--text-primary);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 10px;
    }
    
    /* Warning boxes */
    .stWarning {
        background: linear-gradient(135deg, rgba(120, 53, 15, 0.8) 0%, rgba(146, 64, 14, 0.9) 100%);
        border-left: 5px solid #F59E0B;
        color: var(--text-primary);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 10px;
    }
    
    /* Success boxes */
    .stSuccess {
        background: linear-gradient(135deg, rgba(6, 95, 70, 0.8) 0%, rgba(4, 120, 87, 0.9) 100%);
        border-left: 5px solid #10B981;
        color: var(--text-primary);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 10px;
    }
    
    /* Plotly chart background */
    .js-plotly-plot .plotly, .modebar {
        background-color: #1E293B !important;
        border-radius: 10px;
    }
    
    .js-plotly-plot .plotly .bg {
        fill: #1E293B !important;
    }
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0A1929 0%, #0F172A 100%);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
        padding: 5px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(6, 95, 70, 0.2);
        border-radius: 8px 8px 0 0;
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: var(--text-primary);
        font-weight: 500;
        padding: 10px 20px;
        margin: 0 2px;
        transition: all 0.3s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(16, 185, 129, 0.2);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        border-bottom: 3px solid #34D399 !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }
    
    /* Fix for text colors */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: #F0FDF4 !important;
        font-weight: 600;
    }
    
    .stMarkdown p, .stMarkdown div, .stMarkdown span {
        color: #BBF7D0 !important;
    }
    
    /* Divider styling */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.5), transparent);
        margin: 30px 0;
    }
    
    /* Checkbox styling */
    .stCheckbox > label {
        color: #BBF7D0 !important;
    }
    
    /* Text area */
    .stTextArea > div > div > textarea {
        background: rgba(6, 95, 70, 0.1);
        color: var(--text-primary);
        border-color: rgba(16, 185, 129, 0.3);
        border-radius: 8px;
    }
    
    /* Data editor */
    .stDataFrame {
        background: rgba(6, 95, 70, 0.1);
        border-radius: 10px;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    /* Toast notifications */
    .stToast {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        border: 1px solid rgba(52, 211, 153, 0.5);
    }
    
    /* Select slider */
    .stSelectSlider > div > div {
        background: rgba(6, 95, 70, 0.1);
        border-color: rgba(16, 185, 129, 0.3);
    }
    
    /* Tooltip */
    .stTooltip {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        border: 1px solid rgba(52, 211, 153, 0.5);
    }
    
    /* Avatar */
    .stAvatar {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
    }
    
    /* Badge */
    .stBadge {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-color: #10B981 transparent transparent transparent !important;
    }
    
    /* Code block */
    .stCodeBlock {
        background: rgba(6, 95, 70, 0.2) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 8px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(6, 95, 70, 0.1) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 8px;
        color: #BBF7D0 !important;
    }
    
    .streamlit-expanderContent {
        background: rgba(6, 95, 70, 0.05) !important;
        border: 1px solid rgba(16, 185, 129, 0.2) !important;
        border-radius: 0 0 8px 8px;
    }
    
    /* Multi-select */
    .stMultiSelect > div > div > div {
        background: rgba(6, 95, 70, 0.1);
        border-color: rgba(16, 185, 129, 0.3);
        color: var(--text-primary);
        border-radius: 8px;
    }
    
    /* Color picker */
    .stColorPicker > div > div {
        background: rgba(6, 95, 70, 0.1);
        border-color: rgba(16, 185, 129, 0.3);
        border-radius: 8px;
    }
    
    /* Time input */
    .stTimeInput > div > div > input {
        background: rgba(6, 95, 70, 0.1);
        color: var(--text-primary);
        border-color: rgba(16, 185, 129, 0.3);
        border-radius: 8px;
    }
    
    /* Date input */
    .stDateInput > div > div > input {
        background: rgba(6, 95, 70, 0.1);
        color: var(--text-primary);
        border-color: rgba(16, 185, 129, 0.3);
        border-radius: 8px;
    }
    
    /* Container borders */
    .stContainer {
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 12px;
        padding: 20px;
        background: rgba(6, 95, 70, 0.05);
    }
    
    /* Chat message styling */
    .stChatMessage {
        background: rgba(6, 95, 70, 0.1) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 12px;
    }
    
    /* Table styling */
    table {
        background: rgba(6, 95, 70, 0.1) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 8px;
        overflow: hidden;
    }
    
    th {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%) !important;
        color: white !important;
        font-weight: 600;
    }
    
    td {
        background: rgba(6, 95, 70, 0.05) !important;
        color: #BBF7D0 !important;
        border-color: rgba(16, 185, 129, 0.2) !important;
    }
    
    tr:hover {
        background: rgba(16, 185, 129, 0.1) !important;
    }
    
    /* Image styling */
    .stImage > img {
        border: 2px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Video styling */
    .stVideo > video {
        border: 2px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Audio styling */
    .stAudio > audio {
        border: 2px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        background: rgba(6, 95, 70, 0.1);
    }
    
    /* Balloons animation */
    @keyframes float {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
        100% { transform: translateY(0px); }
    }
    
    .stBalloons {
        animation: float 3s ease-in-out infinite;
    }
    
    /* Snow animation */
    .stSnow {
        color: #10B981 !important;
    }
    
    /* Confetti */
    .stConfetti {
        color: #10B981 !important;
    }
    
    /* Echo container */
    .stEcho {
        background: rgba(6, 95, 70, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        padding: 20px;
    }
    
    /* Placeholder */
    .stPlaceholder {
        background: linear-gradient(135deg, rgba(6, 95, 70, 0.1) 0%, rgba(4, 120, 87, 0.15) 100%);
        border: 2px dashed rgba(16, 185, 129, 0.3);
        border-radius: 12px;
        padding: 40px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.markdown('<h1 class="main-header">NutriMind</h1>', unsafe_allow_html=True)
st.markdown('<p class="slogan">Scan • Track • Grow</p>', unsafe_allow_html=True)

# ========== PROPER GEMINI AI FUNCTION ==========
def analyze_food_with_gemini(food_input, image=None):
    """PROPER Gemini AI Analysis - Get your API key from: https://makersuite.google.com/app/apikey"""
    
    # ⭐⭐⭐ GET YOUR API KEY FROM: https://makersuite.google.com/app/apikey ⭐⭐⭐
    # ⭐⭐⭐ REPLACE THIS WITH YOUR ACTUAL API KEY ⭐⭐⭐
    api_key = "AIzaSyCUFEN7loZiJxffZfG3AubcIRarpigeGUY"
    
    # Show AI thinking message
    thinking_placeholder = st.empty()
    thinking_placeholder.markdown('<div class="ai-thinking">🤖 AI is analyzing your food... Please wait</div>', unsafe_allow_html=True)
    
    try:
        # Check if API key is valid
        if not api_key or "AIzaSy" not in api_key:
            thinking_placeholder.empty()
            st.error("❌ Invalid API key. Please get a new one from: https://makersuite.google.com/app/apikey")
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
                            
                            st.success(f"✅ AI Detected: **{nutrition_data['food_name']}**")
                            return nutrition_data
                    except json.JSONDecodeError as e:
                        st.warning("⚠️ Could not parse AI response. Using fallback.")
        
        # Handle API errors
        if response.status_code == 403:
            st.error("""
            ❌ **API Error 403: Invalid API Key**
            
            Your API key is invalid or disabled. Please:
            1. Get a NEW API key from: https://makersuite.google.com/app/apikey
            2. Replace the api_key in line 87 of this code
            3. Make sure "Generative Language API" is enabled at: https://console.cloud.google.com/apis/library
            """)
        elif response.status_code == 429:
            st.error("❌ API quota exceeded. Try again in a few minutes.")
        else:
            st.warning(f"⚠️ API Error {response.status_code}. Using fallback database.")
        
        # Fallback to database
        return get_fallback_nutrition(food_input)
        
    except requests.exceptions.Timeout:
        thinking_placeholder.empty()
        st.warning("⚠️ AI analysis timed out. Using fallback database.")
        return get_fallback_nutrition(food_input)
    except Exception as e:
        thinking_placeholder.empty()
        st.warning(f"⚠️ Error: {str(e)[:100]}. Using fallback.")
        return get_fallback_nutrition(food_input)

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

# ========== CORE FUNCTIONS ==========
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

# ========== SIDEBAR ==========
with st.sidebar:
    st.markdown("## 👤 User Profile")
    
    if st.session_state.user is None:
        name = st.text_input("Your Name", value=" ")
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
        st.success(f"Welcome, {st.session_state.user['name']}!")
        st.write(f"Age: {st.session_state.user['age']}")
        st.write(f"Gender: {st.session_state.user['gender']}")
        
        if st.button("Logout", type="secondary"):
            st.session_state.user = None
            st.session_state.food_logs = []
            st.session_state.exercise_logs = []
            st.session_state.daily_totals = {'calories': 0, 'protein': 0, 'carbs': 0, 'fats': 0, 'calories_burned': 0, 'water': 0}
            st.rerun()
    
    st.divider()
    st.markdown("## 🎯 Daily Goals")
    
    calories_goal = st.slider("Calories Goal", 1000, 3000, st.session_state.goals['calories'], 100)
    protein_goal = st.slider("Protein Goal (g)", 30, 150, st.session_state.goals['protein'], 5)
    exercise_goal = st.slider("Exercise Goal (min)", 0, 120, st.session_state.goals['exercise_minutes'], 5)
    
    if st.button("Update Goals", key="update_goals"):
        st.session_state.goals['calories'] = calories_goal
        st.session_state.goals['protein'] = protein_goal
        st.session_state.goals['exercise_minutes'] = exercise_goal
        st.success("Goals updated! 💪🏼")
        time.sleep(1)
        st.rerun()
    
    st.divider()
    st.markdown("## 🥗 Diet Preference")
    
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
    
    st.info(f"**Selected:** {st.session_state.diet_preference}")
    
    st.divider()
    st.markdown("## 💧 Water Intake")
    
    water_col1, water_col2 = st.columns(2)
    with water_col1:
        current_water = st.session_state.daily_totals.get('water', 0)
        water_percent = min(100, (current_water / 2000) * 100)
        st.metric("Today", f"{current_water}ml", f"{water_percent:.0f}%")
    
    with water_col2:
        water_to_add = st.selectbox("Add water", [250, 500, 750, 1000], index=0)
        if st.button("💧 Add Water"):
            st.session_state.water_intake += water_to_add
            st.session_state.daily_totals['water'] = st.session_state.water_intake
            st.success(f"Added {water_to_add}ml water!")
            time.sleep(0.5)
            st.rerun()

# ========== MAIN APP ==========
if st.session_state.user is None:
    st.markdown('<div class="nutri-card">', unsafe_allow_html=True)
    st.markdown("## Welcome to NutriMind!")
    st.markdown("""
    **Your AI-powered nutrition assistant that helps you:**
    
    - 📸 **Scan food** with AI analysis
    - 📊 **Track nutrition** in real-time
    - 🏃 **Calculate exercise** needed
    - 🥗 **Get personalized meal recommendations**
    
    *Create a profile or use Demo Mode to get started!*
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
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
        st.markdown(f'<div class="success-toast">{st.session_state.success_message}</div>', unsafe_allow_html=True)
        st.session_state.show_success = False
    
    st.markdown(f"## 👋🏼 Welcome, {st.session_state.user['name']}!")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📝 Log Food", "🏋🏽‍♀️ Exercise", "🥗 Recommendations"])
    
    with tab1:
        # ========== DASHBOARD ==========
        st.header("Your Nutrition Dashboard")
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            cal_percent = min(100, (st.session_state.daily_totals['calories'] / st.session_state.goals['calories']) * 100)
            st.metric("🔥 Calories", f"{st.session_state.daily_totals['calories']}", f"{cal_percent:.0f}% of goal")
        
        with col2:
            pro_percent = min(100, (st.session_state.daily_totals['protein'] / st.session_state.goals['protein']) * 100)
            st.metric("💪🏽 Protein", f"{st.session_state.daily_totals['protein']}g", f"{pro_percent:.0f}% of goal")
        
        with col3:
            st.metric("🌾 Carbs", f"{st.session_state.daily_totals['carbs']}g", f"{(st.session_state.daily_totals['carbs'] / 250 * 100):.0f}%")
        
        with col4:
            st.metric("🥑 Fats", f"{st.session_state.daily_totals['fats']}g", f"{(st.session_state.daily_totals['fats'] / 65 * 100):.0f}%")
        
        with col5:
            exercise_percent = min(100, (len(st.session_state.exercise_logs) * 30 / st.session_state.goals['exercise_minutes']) * 100)
            st.metric("🏃🏽‍♀️ Exercise", f"{len(st.session_state.exercise_logs)} sessions", f"{exercise_percent:.0f}% of goal")
        
        with col6:
            water_percent = min(100, (st.session_state.daily_totals.get('water', 0) / 2000) * 100)
            st.metric("💧 Water", f"{st.session_state.daily_totals.get('water', 0)}ml", f"{water_percent:.0f}%")
        
        # Progress bars
        st.markdown("### Progress Toward Goals")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("**Calories Progress**")
            cal_progress = st.progress(0)
            cal_progress.progress(cal_percent / 100)
            
            st.write("**Protein Progress**")
            pro_progress = st.progress(0)
            pro_progress.progress(pro_percent / 100)
        
        with col_b:
            st.write("**Exercise Progress**")
            ex_progress = st.progress(0)
            ex_progress.progress(exercise_percent / 100)
            
            net_calories = st.session_state.daily_totals['calories'] - st.session_state.daily_totals['calories_burned']
            st.metric("⚖️ Net Calories", f"{net_calories}")
            
            st.write("**Water Progress**")
            water_progress = st.progress(0)
            water_progress.progress(water_percent / 100)
        
        # Weekly chart
        st.markdown("### 📈 Weekly Nutrition & Exercise Trend")
        
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
            color_discrete_map={"Calories": "#10B981", "Protein": "#34D399", "Exercise (min)": "#059669"}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent logs
        col_left, col_right = st.columns(2)
        
        with col_left:
            if st.session_state.food_logs:
                st.markdown("### Recent Food Logs")
                recent_food_logs = st.session_state.food_logs[-3:]
                for log in reversed(recent_food_logs):
                    with st.container():
                        st.markdown(f"""
                        <div class="food-log-item">
                            <strong>🍽️ {log.get('food_name', 'Food')}</strong><br>
                            <small>🔥 {log.get('calories', 0)} cal | 💪🏼 {log.get('protein', 0)}g protein</small><br>
                            <em>💡 {log.get('insight', '')}</em><br>
                            <small style="color: #BBF7D0;">📅 {log.get('date', 'Today')} {log.get('time', '')}</small>
                        </div>
                        """, unsafe_allow_html=True)
                st.info(f"**Total foods logged today:** {len([f for f in st.session_state.food_logs if f.get('date') == datetime.now().strftime('%Y-%m-%d')])}")
            else:
                st.info("No food logged yet. Go to 'Log Food' tab to add food!")
        
        with col_right:
            if st.session_state.exercise_logs:
                st.markdown("### Recent Exercise Logs")
                recent_exercise_logs = st.session_state.exercise_logs[-3:]
                for log in reversed(recent_exercise_logs):
                    with st.container():
                        st.markdown(f"""
                        <div class="exercise-log-item">
                            <strong>🏃🏽‍♀️ {log.get('name', 'Exercise')}</strong><br>
                            <small>⏱️ {log.get('duration', 0)} min | 🔥 {log.get('calories_burned', 0)} cal burned</small><br>
                            <em>📅 {log.get('date', 'Today')} {log.get('time', '')}</em>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No exercise logged yet. Go to 'Exercise' tab to add exercise!")
    
    with tab2:
        # ========== LOG FOOD ==========
        st.header("Log Your Food Intake")
        
        st.markdown("### Choose How to Log Food:")
        
        scan_option = st.radio(
            "Select scanning method:",
            ["📷 Upload Food Image", "🏷️ Upload Food Label", "📝 Manual Food Entry"],
            horizontal=True
        )
        
        if scan_option == "📷 Upload Food Image":
            st.markdown('<div class="scan-option">', unsafe_allow_html=True)
            st.markdown("#### 📸 Upload Food Photo")
            st.markdown("Take a photo of your meal and get AI-powered nutrition analysis")
            
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
                    st.markdown("**Image Details:**")
                    st.write(f"Format: {image.format}")
                    st.write(f"Size: {image.size[0]}x{image.size[1]} pixels")
                    st.write(f"Mode: {image.mode}")
                
                if st.button("Analyze with AI 🔍", type="primary", use_container_width=True):
                    # Use the PROPER food analysis function
                    nutrition = analyze_food_with_gemini("uploaded food image", image)
                    nutrition['scan_type'] = "Image"
                    
                    # Store for saving
                    st.session_state.current_analyzed_food = nutrition
                    
                    st.markdown(f"### 🍽️ {nutrition['food_name']}")
                    nutri_cols = st.columns(4)
                    with nutri_cols[0]:
                        st.metric("Calories", nutrition['calories'])
                    with nutri_cols[1]:
                        st.metric("Protein", f"{nutrition['protein']}g")
                    with nutri_cols[2]:
                        st.metric("Carbs", f"{nutrition['carbs']}g")
                    with nutri_cols[3]:
                        st.metric("Fats", f"{nutrition['fats']}g")
                    
                    st.info(f"💡 **Insight:** {nutrition['insight']}")
            
            # Save button
            if st.session_state.current_analyzed_food:
                st.markdown("### Adjust Portion Size")
                portion = st.select_slider(
                    "Select portion size:",
                    options=["Small", "Medium", "Large", "Extra"],
                    value="Medium"
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
                
                st.info(f"**{portion} Portion:** {adjusted_nutrition['calories']} calories, {adjusted_nutrition['protein']}g protein")
                
                if st.button("✅ Save This Food", key="save_image_food"):
                    saved = save_food_to_session(adjusted_nutrition)
                    if saved:
                        st.balloons()
                        st.session_state.current_analyzed_food = None
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        elif scan_option == "🏷️ Upload Food Label":
            st.markdown('<div class="scan-option">', unsafe_allow_html=True)
            st.markdown("#### 🏷️ Upload Food Label")
            st.markdown("Upload a photo of nutrition facts label for precise analysis")
            
            uploaded_label = st.file_uploader(
                "Upload label image (JPG, PNG)", 
                type=["jpg", "jpeg", "png"],
                key="label_upload",
                label_visibility="collapsed"
            )
            
            if uploaded_label is not None:
                label_image = Image.open(uploaded_label)
                st.image(label_image, caption="Food Label", width=300)
                
                if st.button("Extract Nutrition Facts", type="primary"):
                    with st.spinner("📊 Extracting nutrition facts from label..."):
                        time.sleep(2)
                        
                        label_nutrition = analyze_food_with_gemini("nutrition label", label_image)
                        label_nutrition['scan_type'] = "Label"
                        
                        st.session_state.current_analyzed_food = label_nutrition
                        
                        st.markdown(f"### 🏷️ {label_nutrition['food_name']}")
                        nutri_cols = st.columns(4)
                        with nutri_cols[0]:
                            st.metric("Calories", label_nutrition['calories'])
                        with nutri_cols[1]:
                            st.metric("Protein", f"{label_nutrition['protein']}g")
                        with nutri_cols[2]:
                            st.metric("Carbs", f"{label_nutrition['carbs']}g")
                        with nutri_cols[3]:
                            st.metric("Fats", f"{label_nutrition['fats']}g")
            
            # Save button
            if st.session_state.current_analyzed_food:
                if st.button("✅ Save from Label", key="save_label_food"):
                    saved = save_food_to_session(st.session_state.current_analyzed_food)
                    if saved:
                        st.balloons()
                        st.session_state.current_analyzed_food = None
                        st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        else:  # Manual Food Entry
            st.markdown('<div class="scan-option">', unsafe_allow_html=True)
            st.markdown("#### 📝 Manual Food Entry")
            st.markdown("Enter food details manually")
            
            food_input = st.text_input(
                "Enter food name:",
                placeholder="e.g., Masala Dosa, Butter Chicken, Apple, Chapati...",
                key="manual_food_input"
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
                        
                        st.markdown(f"### 🍽️ {nutrition['food_name']}")
                        nutri_cols = st.columns(4)
                        with nutri_cols[0]:
                            st.metric("Calories", nutrition['calories'])
                        with nutri_cols[1]:
                            st.metric("Protein", f"{nutrition['protein']}g")
                        with nutri_cols[2]:
                            st.metric("Carbs", f"{nutrition['carbs']}g")
                        with nutri_cols[3]:
                            st.metric("Fats", f"{nutrition['fats']}g")
                        
                        st.info(f"💡 **Insight:** {nutrition['insight']}")
                
                # Save button
                if st.session_state.current_analyzed_food:
                    st.markdown("### Adjust Portion Size")
                    portion = st.select_slider(
                        "Select portion size:",
                        options=["Small", "Medium", "Large", "Extra"],
                        value="Medium"
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
                    
                    st.info(f"**{portion} Portion:** {adjusted_nutrition['calories']} calories, {adjusted_nutrition['protein']}g protein")
                    
                    if st.button("✅ Save This Food", key="save_manual_food"):
                        saved = save_food_to_session(adjusted_nutrition)
                        if saved:
                            st.balloons()
                            st.session_state.current_analyzed_food = None
                            st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        # ========== EXERCISE TRACKER ==========
        st.header("Exercise Calculator & Tracker")
        
        if st.session_state.daily_totals['calories'] > 0:
            st.info(f"Today you've consumed **{st.session_state.daily_totals['calories']} calories**. Here's how to burn them:")
            
            exercises = get_exercise_suggestions(st.session_state.daily_totals['calories'])
            
            for ex in exercises:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"**{ex['name']}**")
                with col2:
                    st.write(f"{ex['duration']} min")
                with col3:
                    if st.button("✅ Log", key=f"log_ex_{ex['name']}"):
                        exercise_log = {
                            "name": ex['name'],
                            "duration": ex['duration'],
                            "calories_burned": ex['duration'] * ex['calories_per_min'],
                            "time": datetime.now().strftime("%H:%M"),
                            "date": datetime.now().strftime("%Y-%m-%d")
                        }
                        
                        saved = save_exercise_to_session(exercise_log)
                        if saved:
                            st.success(f"✅ {ex['name']} logged!")
                            st.rerun()
            
            st.divider()
            
            st.subheader("Log Custom Exercise")
            col1, col2 = st.columns(2)
            
            with col1:
                exercise_types = ["Running", "Walking", "Cycling", "Gym", "Yoga", "Swimming", "Dancing", "Other"]
                custom_exercise = st.selectbox("Select exercise type", exercise_types)
                if custom_exercise == "Other":
                    custom_exercise = st.text_input("Enter exercise name")
                
                duration = st.slider("Duration (minutes)", 5, 180, 30, 5)
            
            with col2:
                intensity = st.select_slider(
                    "Intensity Level",
                    options=["Light", "Moderate", "High", "Very High"]
                )
                
                intensity_multiplier = {"Light": 5, "Moderate": 8, "High": 12, "Very High": 15}
                calories_burned = duration * intensity_multiplier[intensity]
                
                st.metric("Estimated Calories Burned", f"{calories_burned}")
                
                if st.button("Log Custom Exercise", type="primary", use_container_width=True):
                    exercise_log = {
                        "name": custom_exercise,
                        "duration": duration,
                        "intensity": intensity,
                        "calories_burned": calories_burned,
                        "time": datetime.now().strftime("%H:%M"),
                        "date": datetime.now().strftime("%Y-%m-%d")
                    }
                    
                    saved = save_exercise_to_session(exercise_log)
                    if saved:
                        st.success(f"✅ {custom_exercise} logged for {duration} minutes!")
                        st.balloons()
                        st.rerun()
        
        else:
            st.info("Log some food first to see exercise suggestions!")
        
        # Exercise history
        st.markdown("---")
        st.subheader("Today's Exercise History")
        
        if st.session_state.exercise_logs:
            today_exercises = [ex for ex in st.session_state.exercise_logs 
                              if ex.get('date') == datetime.now().strftime("%Y-%m-%d")]
            
            if today_exercises:
                total_calories_burned = sum([ex.get('calories_burned', 0) for ex in today_exercises])
                total_minutes = sum([ex.get('duration', 0) for ex in today_exercises])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Calories Burned", f"{total_calories_burned}")
                with col2:
                    st.metric("Total Exercise Time", f"{total_minutes} min")
                
                for ex in today_exercises:
                    with st.container():
                        st.markdown(f"""
                        <div class="exercise-log-item">
                            <strong>🏃 {ex.get('name', 'Exercise')}</strong><br>
                            <small>⏱️ {ex.get('duration', 0)} min | 🔥 {ex.get('calories_burned', 0)} cal burned</small><br>
                            <em>⚡ Intensity: {ex.get('intensity', 'Moderate')} | 📅 {ex.get('time', '')}</em>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No exercises logged today yet.")
        else:
            st.info("No exercises logged yet. Start logging to see your progress!")
    
    with tab4:
        # ========== RECOMMENDATIONS ==========
        st.header("Personalized Meal Recommendations")
        
        st.markdown(f"### 🥗 Based on your diet preference: **{st.session_state.diet_preference}**")
        
        remaining_calories = st.session_state.goals['calories'] - st.session_state.daily_totals['calories']
        remaining_protein = st.session_state.goals['protein'] - st.session_state.daily_totals['protein']
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Remaining Calories", f"{max(0, remaining_calories)}")
        with col2:
            st.metric("Remaining Protein", f"{max(0, remaining_protein)}g")
        
        meal_time = st.selectbox("Select meal time:", ["Breakfast", "Lunch", "Dinner", "Snack"])
        
        suggestions = get_meal_suggestions(
            meal_time, 
            st.session_state.diet_preference, 
            remaining_calories, 
            remaining_protein
        )
        
        st.markdown(f"### 🍽️ {meal_time} Suggestions:")
        
        for i, suggestion in enumerate(suggestions):
            with st.container():
                st.markdown(f"""
                <div class="meal-suggestion-card">
                    <strong>{suggestion}</strong><br>
                    <small>Recommended based on your {st.session_state.diet_preference} diet</small>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Quick Add to Today's Log", key=f"add_meal_{i}"):
                    import re
                    cal_match = re.search(r'\((\d+) cal', suggestion)
                    protein_match = re.search(r', (\d+)g protein', suggestion)
                    
                    calories = int(cal_match.group(1)) if cal_match else 300
                    protein = int(protein_match.group(1)) if protein_match else 15
                    
                    food_name = suggestion.split(" (")[0].replace("🍳 ", "").replace("🥚 ", "").replace("🍗 ", "").replace("🧀 ", "").replace("🥣 ", "").replace("🐟 ", "").replace("🥘 ", "").replace("🍚 ", "").replace("🥗 ", "").replace("🍛 ", "")
                    
                    food_data = {
                        "food_name": food_name,
                        "calories": calories,
                        "protein": protein,
                        "carbs": calories * 0.5 / 4,
                        "fats": calories * 0.25 / 9,
                        "insight": f"Recommended {meal_time} for {st.session_state.diet_preference} diet",
                        "meal_time": meal_time
                    }
                    
                    saved = save_food_to_session(food_data)
                    if saved:
                        st.success(f"✅ {food_name} added to your food log!")
                        st.rerun()
        
        st.markdown("---")
        
        # Nutrition tips
        st.subheader("💡 Personalized Nutrition Tips")
        
        if remaining_calories < 0:
            st.warning("⚠️ You've exceeded your calorie goal for today! Consider lighter meals or extra exercise.")
        elif remaining_calories < 300:
            st.info("🍎 You have few calories left. Opt for light, nutrient-dense snacks.")
        else:
            st.success("🎯 You're on track! You still have room for a satisfying meal.")
        
        if remaining_protein < 0:
            st.warning("⚠️ You've exceeded your protein goal. Great for muscle building!")
        elif remaining_protein < 15:
            st.info("💪 Add a protein-rich food to meet your daily target.")
        else:
            st.success("🏋🏽‍♀️ Good protein balance. Keep it up!")

# ========== FOOTER ==========
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #10B981; padding: 20px;">
        <p><strong>NutriMind</strong> | Scan.Track.Grow 🥗🧠🏃🏽‍♀️💪🏽</p>
        <p><strong>Built for Google TechSprint</strong></p>
        <p style="font-size: 0.9em;">Team euphoria</p>
    </div>
    """,
    unsafe_allow_html=True
)

