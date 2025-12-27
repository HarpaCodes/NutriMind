# app.py - NutriMind with FIXED Gemini AI 2.5 Flash Lite
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

# Custom CSS for dark teal theme
st.markdown("""
<style>
    /* Dark Teal Theme Variables */
    :root {
        --teal-primary: #006D6F;
        --teal-secondary: #008080;
        --teal-light: #00A0A0;
        --teal-dark: #004D4F;
        --teal-accent: #00C9C9;
        --bg-dark: #0A1929;
        --bg-card: #132F4C;
        --text-primary: #E6F7FF;
        --text-secondary: #B3D9FF;
        --border-color: #006D6F;
    }
    
    /* Main Header with teal gradient */
    .main-header {
        font-size: 3rem;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #00C9C9 0%, #006D6F 25%, #008080 50%, #00A0A0 75%, #004D4F 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        letter-spacing: -0.5px;
        padding: 10px 0;
    }
    
    .nutri-card {
        background: linear-gradient(135deg, #004D4F 0%, #006D6F 100%);
        color: var(--text-primary);
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        border: 1px solid var(--border-color);
    }
    
    .scan-option {
        text-align: center;
        padding: 20px;
        border: 2px dashed #00C9C9;
        border-radius: 10px;
        margin: 10px 0;
        transition: all 0.3s;
        background: var(--bg-card);
        color: var(--text-primary);
        border-color: var(--teal-accent);
    }
    
    /* Food log items with teal theme */
    .food-log-item {
        background: linear-gradient(135deg, #004D4F 0%, #006D6F 100%);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #00C9C9;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color);
    }
    
    /* Exercise log items with teal theme */
    .exercise-log-item {
        background: linear-gradient(135deg, #004D4F 0%, #006D6F 100%);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #00A0A0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color);
    }
    
    /* Fix for text colors */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown p, .stMarkdown div {
        color: var(--text-primary) !important;
    }
    
    .slogan {
        text-align: center;
        font-size: 1.2rem;
        color: #00C9C9;
        font-weight: 600;
        letter-spacing: 1px;
        margin: 10px 0 30px 0;
    }
    
    .success-toast {
        background: linear-gradient(135deg, #006D6F 0%, #00A0A0 100%);
        color: var(--text-primary);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        animation: fadeIn 0.5s;
        box-shadow: 0 4px 12px rgba(0, 201, 201, 0.3);
        border: 1px solid var(--teal-accent);
    }
    
    .ai-thinking {
        background: linear-gradient(135deg, #004D4F 0%, #006D6F 100%);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #00C9C9;
        color: var(--text-primary);
        border: 1px solid var(--border-color);
    }
    
    /* MEAL SUGGESTION CARD - FIXED FOR DARK MODE */
    .meal-suggestion-card {
        padding: 15px;
        background: linear-gradient(135deg, #004D4F 0%, #006D6F 100%);
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #00C9C9;
        border: 1px solid var(--border-color);
    }
    
    .meal-suggestion-card strong {
        color: #FFFFFF !important;
        font-size: 1.1em;
    }
    
    .meal-suggestion-card small {
        color: #B3D9FF !important;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Progress bars with teal theme */
    .stProgress > div > div > div > div {
        background-color: #00C9C9;
    }
    
    /* Buttons with teal theme */
    .stButton > button {
        background: linear-gradient(135deg, #006D6F 0%, #008080 100%);
        color: white;
        border: 1px solid #00A0A0;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #008080 0%, #00A0A0 100%);
        border-color: #00C9C9;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1lcbmhc {
        background-color: var(--bg-dark);
    }
    
    /* Metric cards */
    .stMetric {
        background: linear-gradient(135deg, #004D4F 0%, #006D6F 100%);
        padding: 10px;
        border-radius: 10px;
        border: 1px solid var(--border-color);
    }
    
    /* Radio buttons with teal theme */
    .stRadio > div {
        background: var(--bg-card);
        padding: 10px;
        border-radius: 10px;
        border: 1px solid var(--border-color);
    }
    
    /* Selectbox and slider styling */
    .stSelectbox, .stSlider {
        background: var(--bg-card);
    }
    
    /* Ensure text is visible in all modes */
    div[data-testid="stVerticalBlock"] > div > div > div > div {
        color: var(--text-primary) !important;
    }
    
    /* Main background */
    .stApp {
        background-color: var(--bg-dark);
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(135deg, #004D4F 0%, #006D6F 100%);
        border-radius: 8px 8px 0 0;
        border: 1px solid var(--border-color);
        color: var(--text-primary);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #006D6F 0%, #008080 100%) !important;
        color: white !important;
        border-bottom: 2px solid #00C9C9 !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background: var(--bg-card);
        color: var(--text-primary);
        border-color: var(--border-color);
    }
    
    /* File uploader */
    .stFileUploader > div > div {
        background: var(--bg-card);
        border-color: var(--border-color);
    }
    
    /* Info boxes */
    .stInfo {
        background: linear-gradient(135deg, #004D4F 0%, #006D6F 100%);
        border-left: 4px solid #00C9C9;
        color: var(--text-primary);
        border: 1px solid var(--border-color);
    }
    
    /* Warning boxes */
    .stWarning {
        background: linear-gradient(135deg, #4D3C00 0%, #6F5D00 100%);
        border-left: 4px solid #FFD700;
        color: var(--text-primary);
        border: 1px solid #FFD700;
    }
    
    /* Success boxes */
    .stSuccess {
        background: linear-gradient(135deg, #004D2E 0%, #006D47 100%);
        border-left: 4px solid #00FF95;
        color: var(--text-primary);
        border: 1px solid #00FF95;
    }
    
    /* Plotly chart background */
    .js-plotly-plot .plotly, .modebar {
        background-color: var(--bg-card) !important;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.markdown('<h1 class="main-header">NutriMind</h1>', unsafe_allow_html=True)
st.markdown('<p class="slogan">Scan • Track • Grow</p>', unsafe_allow_html=True)

# ========== FIXED GEMINI AI FUNCTION WITH DIRECT API KEY ==========
def analyze_food_with_gemini(food_input, image=None):
    """WINNING FIX: Food analysis with DIRECT API KEY - NO SECRETS NEEDED"""
    try:
        # ⭐⭐⭐ WINNING FIX - YOUR API KEY IS HERE DIRECTLY ⭐⭐⭐
        api_key = "AIzaSyC-O7lQBS27JHP9zHaOCD20LmwzeW0QmwA"
        
        # Verify key is valid
        if not api_key or "AIzaSy" not in api_key:
            st.error("❌ API Key not properly configured!")
            return get_fallback_nutrition(food_input)
        
        # Show AI thinking message
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown('<div class="ai-thinking">🤖 AI is analyzing your food image... Please wait</div>', unsafe_allow_html=True)
        
        # Prepare the prompt
        if image:
            # Convert image to base64
            buffered = io.BytesIO()
            # Convert image to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            image.save(buffered, format="JPEG", quality=85)
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            prompt = """Analyze this food image and provide nutrition information.
            FIRST identify what food/dish this is.
            Then provide nutrition facts in this EXACT JSON format:
            {
                "food_name": "Specific Name of Food",
                "calories": number,
                "protein": number,
                "carbs": number,
                "fats": number,
                "insight": "Brief nutritional insight about this food"
            }
            
            IMPORTANT: Return ONLY the JSON object, no additional text.
            Use realistic values for common foods. If uncertain, provide reasonable estimates."""
            
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
                    "temperature": 0.2,
                    "maxOutputTokens": 500,
                }
            }
        else:
            prompt = f"""Analyze this food: {food_input}
            Identify what food/dish this is and provide accurate nutrition facts.
            Return in this EXACT JSON format:
            {{
                "food_name": "Specific Name of Food",
                "calories": number,
                "protein": number,
                "carbs": number,
                "fats": number,
                "insight": "Brief nutritional insight"
            }}
            
            IMPORTANT: Return ONLY the JSON object, no additional text.
            Use realistic values for common foods."""
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.2,
                    "maxOutputTokens": 500,
                }
            }
        
        # Make API request with timeout
        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={api_key}",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            thinking_placeholder.empty()  # Remove thinking message
            
            if response.status_code == 200:
                result = response.json()
                if "candidates" in result and len(result["candidates"]) > 0:
                    response_text = result["candidates"][0]["content"]["parts"][0]["text"]
                    
                    # Clean the response text
                    response_text = response_text.strip()
                    
                    # Remove markdown code blocks if present
                    if response_text.startswith("```json"):
                        response_text = response_text[7:]
                    if response_text.endswith("```"):
                        response_text = response_text[:-3]
                    response_text = response_text.strip()
                    
                    # Try to parse JSON
                    try:
                        nutrition_data = json.loads(response_text)
                        
                        # Validate required fields
                        required_fields = ["food_name", "calories", "protein", "carbs", "fats", "insight"]
                        if all(field in nutrition_data for field in required_fields):
                            # Ensure numeric fields are numbers
                            nutrition_data["calories"] = float(nutrition_data["calories"])
                            nutrition_data["protein"] = float(nutrition_data["protein"])
                            nutrition_data["carbs"] = float(nutrition_data["carbs"])
                            nutrition_data["fats"] = float(nutrition_data["fats"])
                            
                            # Round to integers
                            for key in ["calories", "protein", "carbs", "fats"]:
                                nutrition_data[key] = int(round(nutrition_data[key]))
                            
                            st.success(f"✅ AI successfully identified: **{nutrition_data['food_name']}**")
                            return nutrition_data
                        else:
                            st.warning("⚠️ AI response missing some fields. Using fallback.")
                    except json.JSONDecodeError as e:
                        st.warning(f"⚠️ Could not parse AI response as JSON. Using fallback.")
            
            # If API response is not successful
            st.warning(f"⚠️ API response not as expected. Status: {response.status_code}")
            
        except requests.exceptions.Timeout:
            thinking_placeholder.empty()
            st.warning("⚠️ AI analysis timed out. Using fallback database.")
        except requests.exceptions.RequestException as e:
            thinking_placeholder.empty()
            st.warning(f"⚠️ Network error: {str(e)[:100]}. Using fallback database.")
        
        # If any error, use fallback
        return get_fallback_nutrition(food_input)
        
    except Exception as e:
        thinking_placeholder.empty()
        st.warning(f"⚠️ AI analysis error: {str(e)[:100]}. Using fallback database.")
        return get_fallback_nutrition(food_input)

def get_fallback_nutrition(food_name):
    """Comprehensive fallback nutrition database - NO API needed"""
    food_db = {
        # Indian Foods
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
        
        # Curries
        "butter chicken": {"food_name": "Butter Chicken", "calories": 450, "protein": 30, "carbs": 15, "fats": 30, "insight": "Creamy tomato-based chicken curry"},
        "paneer butter": {"food_name": "Paneer Butter Masala", "calories": 400, "protein": 22, "carbs": 20, "fats": 25, "insight": "Creamy cottage cheese curry"},
        "chicken curry": {"food_name": "Chicken Curry", "calories": 350, "protein": 25, "carbs": 10, "fats": 20, "insight": "Spicy chicken in gravy"},
        "dal": {"food_name": "Dal Tadka", "calories": 150, "protein": 9, "carbs": 22, "fats": 4, "insight": "Tempered lentil soup, rich in protein"},
        "sambar": {"food_name": "Sambar", "calories": 100, "protein": 5, "carbs": 18, "fats": 3, "insight": "South Indian lentil stew with vegetables"},
        
        # Fruits
        "banana": {"food_name": "Banana", "calories": 105, "protein": 1.3, "carbs": 27, "fats": 0.3, "insight": "Rich in potassium and quick energy"},
        "apple": {"food_name": "Apple", "calories": 95, "protein": 0.5, "carbs": 25, "fats": 0.3, "insight": "High in fiber and antioxidants"},
        "orange": {"food_name": "Orange", "calories": 62, "protein": 1.2, "carbs": 15, "fats": 0.2, "insight": "Excellent source of Vitamin C"},
        "mango": {"food_name": "Mango", "calories": 150, "protein": 1.1, "carbs": 40, "fats": 0.6, "insight": "Rich in Vitamin A and C"},
        "grapes": {"food_name": "Grapes", "calories": 69, "protein": 0.7, "carbs": 18, "fats": 0.2, "insight": "Natural sugars with antioxidants"},
        
        # Protein Sources
        "egg": {"food_name": "Egg (Boiled)", "calories": 78, "protein": 6, "carbs": 0.6, "fats": 5, "insight": "Complete protein with all essential amino acids"},
        "chicken": {"food_name": "Chicken Breast", "calories": 165, "protein": 31, "carbs": 0, "fats": 3.6, "insight": "Lean protein for muscle building"},
        "fish": {"food_name": "Fish (Grilled)", "calories": 206, "protein": 22, "carbs": 0, "fats": 12, "insight": "Rich in Omega-3 fatty acids"},
        "paneer": {"food_name": "Paneer", "calories": 265, "protein": 18, "carbs": 1.2, "fats": 20, "insight": "Indian cottage cheese, high in calcium"},
        "tofu": {"food_name": "Tofu", "calories": 76, "protein": 8, "carbs": 2, "fats": 4, "insight": "Plant-based protein from soy"},
        
        # Snacks & Fast Food
        "pizza": {"food_name": "Pizza Slice", "calories": 285, "protein": 12, "carbs": 36, "fats": 10, "insight": "Contains carbs, protein and fats"},
        "burger": {"food_name": "Cheese Burger", "calories": 354, "protein": 15, "carbs": 29, "fats": 20, "insight": "Fast food with moderate protein"},
        "samosa": {"food_name": "Samosa", "calories": 300, "protein": 4, "carbs": 35, "fats": 16, "insight": "Fried pastry with potato filling"},
        "pakora": {"food_name": "Pakora", "calories": 200, "protein": 5, "carbs": 20, "fats": 10, "insight": "Vegetable fritters, deep fried"},
        
        # Dairy
        "milk": {"food_name": "Milk (1 cup)", "calories": 150, "protein": 8, "carbs": 12, "fats": 8, "insight": "Rich in calcium and protein"},
        "curd": {"food_name": "Curd/Yogurt", "calories": 150, "protein": 8, "carbs": 11, "fats": 8, "insight": "Probiotic-rich for gut health"},
        "cheese": {"food_name": "Cheese", "calories": 113, "protein": 7, "carbs": 1, "fats": 9, "insight": "High in calcium and protein"},
        
        # Beverages
        "smoothie": {"food_name": "Fruit Smoothie", "calories": 200, "protein": 8, "carbs": 30, "fats": 5, "insight": "Blended fruits with nutrients"},
        "juice": {"food_name": "Orange Juice", "calories": 112, "protein": 2, "carbs": 26, "fats": 0.5, "insight": "Vitamin C rich beverage"},
        "coffee": {"food_name": "Coffee", "calories": 2, "protein": 0.3, "carbs": 0, "fats": 0, "insight": "Low calorie caffeine source"},
        "tea": {"food_name": "Tea", "calories": 2, "protein": 0, "carbs": 0.5, "fats": 0, "insight": "Low calorie beverage with antioxidants"},
        
        # Common foods
        "bread": {"food_name": "Bread Slice", "calories": 79, "protein": 3, "carbs": 15, "fats": 1, "insight": "Basic carbohydrate source"},
        "pasta": {"food_name": "Pasta", "calories": 220, "protein": 8, "carbs": 43, "fats": 1, "insight": "Carb-rich Italian dish"},
        "sandwich": {"food_name": "Vegetable Sandwich", "calories": 250, "protein": 8, "carbs": 40, "fats": 6, "insight": "Quick meal with vegetables"},
        "salad": {"food_name": "Green Salad", "calories": 100, "protein": 4, "carbs": 15, "fats": 3, "insight": "Healthy vegetable mix"},
        
        # New additions
        "rice bowl": {"food_name": "Steamed Rice Bowl", "calories": 240, "protein": 4.5, "carbs": 53, "fats": 0.5, "insight": "Simple carbohydrates for energy"},
        "chicken salad": {"food_name": "Chicken Salad", "calories": 320, "protein": 35, "carbs": 12, "fats": 15, "insight": "Lean protein with vegetables"},
        "protein shake": {"food_name": "Protein Shake", "calories": 180, "protein": 25, "carbs": 12, "fats": 3, "insight": "Quick protein supplement"},
        "oatmeal": {"food_name": "Oatmeal", "calories": 150, "protein": 5, "carbs": 27, "fats": 3, "insight": "High fiber breakfast"},
        "fried rice": {"food_name": "Vegetable Fried Rice", "calories": 380, "protein": 8, "carbs": 60, "fats": 12, "insight": "Stir-fried rice with vegetables"},
    }
    
    if not food_name or food_name == "" or food_name == "food image" or food_name == "nutrition label":
        return {
            "food_name": "General Food",
            "calories": 200,
            "protein": 10,
            "carbs": 25,
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
        st.metric("Today's Water", f"{current_water}ml", f"{water_percent:.0f}%")
    
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
            color_discrete_map={"Calories": "#FF6B6B", "Protein": "#118AB2", "Exercise (min)": "#FFD166"}
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
                            <small style="color: #B3D9FF;">📅 {log.get('date', 'Today')} {log.get('time', '')}</small>
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
                    # Use the improved food analysis function
                    nutrition = analyze_food_with_gemini("uploaded food image", image)
                    nutrition['scan_type'] = "Image"
                    
                    # Store for saving
                    st.session_state.current_analyzed_food = nutrition
                    
                    # The success message is already shown inside analyze_food_with_gemini function
                    # So no need to show it again here
                    
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
                        
                        # Success message shown inside function
                        
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
                        
                        # Success message shown inside function
                        
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
    <div style="text-align: center; color: #00C9C9; padding: 20px;">
        <p><strong>NutriMind</strong> | Scan.Track.Grow 🥗🧠🏃🏽‍♀️💪🏽</p>
        <p><strong>Built for Google TechSprint</strong></p>
        <p style="font-size: 0.9em;">Team euphoria</p>
    </div>
    """,
    unsafe_allow_html=True
)

