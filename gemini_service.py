# gemini_service.py
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables (for local .env file)
load_dotenv()

def init_gemini():
    """Initialize the Gemini API client with the API key."""
    # Try to get API key from environment variable
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("Warning: GEMINI_API_KEY not found in environment.")
        print("The app will use demo nutrition data.")
        return False
    
    try:
        # Configure the API key for the library
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        return False

def analyze_food_text(food_name):
    """
    Analyze a food item using Gemini AI based on text description.
    
    Args:
        food_name (str): The name of the food to analyze.
        
    Returns:
        dict: Nutrition information including calories, protein, carbs, fats, and an insight.
    """
    # First, try to use the actual Gemini API
    if init_gemini():
        try:
            # Initialize the model (using a text model since we have no image)
            model = genai.GenerativeModel('gemini-pro')
            
            # Create a detailed prompt for Indian food context
            prompt = f"""
            Analyze this food item for nutrition: "{food_name}"
            
            Consider this is for a typical Indian meal portion.
            
            Return ONLY a valid JSON object with this exact structure:
            {{
                "food_name": "{food_name}",
                "calories": number,
                "protein": number,
                "carbs": number, 
                "fats": number,
                "insight": "one short, helpful sentence about this food's nutrition value"
            }}
            
            Example for "Chapati":
            {{
                "food_name": "Chapati",
                "calories": 120,
                "protein": 3,
                "carbs": 20,
                "fats": 2,
                "insight": "Good source of carbohydrates for energy, low in fat."
            }}
            
            Ensure all values are numbers (not strings) for calories, protein, carbs, and fats.
            """
            
            # Generate the response
            response = model.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON from the response (it might have markdown or extra text)
            import json
            import re
            
            # Find JSON pattern in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                nutrition_data = json.loads(json_match.group())
                
                # Validate the data has required fields
                required_fields = ["food_name", "calories", "protein", "carbs", "fats", "insight"]
                if all(field in nutrition_data for field in required_fields):
                    return nutrition_data
            
            # If JSON parsing fails, fall back to demo data
            print(f"Could not parse Gemini response for: {food_name}")
            
        except Exception as e:
            print(f"Gemini API error for '{food_name}': {e}")
    
    # Fallback: Use demo data if API fails or is not configured
    return get_demo_nutrition(food_name)

def get_demo_nutrition(food_name):
    """
    Provide demo nutrition data for common foods when Gemini API is unavailable.
    
    Args:
        food_name (str): The name of the food.
        
    Returns:
        dict: Predefined nutrition information.
    """
    food_db = {
        "apple": {"calories": 95, "protein": 0.5, "carbs": 25, "fats": 0.3, 
                  "insight": "Low calorie fruit rich in fiber and vitamins."},
        "banana": {"calories": 105, "protein": 1.3, "carbs": 27, "fats": 0.4,
                   "insight": "Good source of potassium and quick energy."},
        "rice": {"calories": 200, "protein": 4, "carbs": 45, "fats": 1,
                 "insight": "Primary carbohydrate source, provides sustained energy."},
        "chapati": {"calories": 120, "protein": 3, "carbs": 20, "fats": 2,
                    "insight": "Whole wheat provides fiber and sustained energy."},
        "dal": {"calories": 150, "protein": 8, "carbs": 25, "fats": 3,
                "insight": "Excellent plant-based protein and fiber source."},
        "chicken curry": {"calories": 350, "protein": 25, "carbs": 10, "fats": 20,
                          "insight": "High quality protein, watch portion size for fats."},
        "paneer": {"calories": 280, "protein": 18, "carbs": 8, "fats": 20,
                   "insight": "Rich in protein and calcium, moderate in fats."},
        "egg": {"calories": 78, "protein": 6, "carbs": 0.6, "fats": 5,
                "insight": "Complete protein source with essential nutrients."},
        "milk": {"calories": 150, "protein": 8, "carbs": 12, "fats": 8,
                 "insight": "Good source of calcium, protein, and vitamins."},
        "butter chicken": {"calories": 450, "protein": 30, "carbs": 15, "fats": 30,
                           "insight": "High in protein but also high in calories and fats."},
        "biryani": {"calories": 400, "protein": 20, "carbs": 60, "fats": 12,
                    "insight": "Balanced meal with carbs, protein, but can be calorie-dense."},
        "idli": {"calories": 80, "protein": 3, "carbs": 15, "fats": 0.5,
                 "insight": "Light, fermented food that's easy to digest."},
        "dosa": {"calories": 150, "protein": 4, "carbs": 25, "fats": 4,
                 "insight": "Fermented crepe, good source of carbohydrates."},
        "sambar": {"calories": 100, "protein": 5, "carbs": 15, "fats": 3,
                   "insight": "Lentil-based stew rich in protein and vegetables."}
    }
    
    # Try to find exact or partial match
    food_lower = food_name.lower()
    
    # Check for exact match
    if food_lower in food_db:
        result = food_db[food_lower].copy()
        result["food_name"] = food_name
        return result
    
    # Check for partial matches (e.g., "chicken" in "butter chicken")
    # FIXED LINE 73: Added the missing colon
    for key, value in food_db.items():  # ← THIS LINE WAS MISSING THE COLON
        if key in food_lower or food_lower in key:
            result = value.copy()
            result["food_name"] = food_name
            return result
    
    # Default fallback for unknown foods
    return {
        "food_name": food_name,
        "calories": 200,
        "protein": 10,
        "carbs": 25,
        "fats": 8,
        "insight": "Estimated nutrition values based on typical foods."
    }

# For future use: Function to analyze food from image (when you have Storage)
def analyze_food_image(image_bytes=None, image_url=None):
    """
    Analyze food from an image using Gemini Vision.
    Note: This requires the 'gemini-pro-vision' model and proper image data.
    
    Args:
        image_bytes (bytes): Raw image bytes.
        image_url (str): URL to the image (if stored online).
        
    Returns:
        dict: Nutrition information from the image analysis.
    """
    if not init_gemini():
        return {"error": "Gemini API not configured", "food_name": "Unknown Food"}
    
    try:
        # For now, this is a placeholder for when you add image functionality
        # You would need to use gemini-pro-vision model and pass the image
        print("Image analysis is ready to implement when you enable Firebase Storage.")
        return {
            "food_name": "Image Analysis Pending",
            "calories": 0,
            "protein": 0,
            "carbs": 0,
            "fats": 0,
            "insight": "Enable Firebase Storage to use camera analysis."
        }
        
    except Exception as e:
        print(f"Image analysis error: {e}")
        return get_demo_nutrition("Unknown Food")

# Helper function for exercise suggestions
def get_exercise_suggestions(calories):
    """
    Generate exercise suggestions based on calories consumed.
    
    Args:
        calories (int): Number of calories to burn.
        
    Returns:
        list: Exercise options with duration.
    """
    exercises = [
        {"name": "🏃 Jogging", "duration": max(5, calories // 10), "calories_per_min": 10},
        {"name": "🚶 Walking", "duration": max(10, calories // 5), "calories_per_min": 5},
        {"name": "🚴 Cycling", "duration": max(8, calories // 12), "calories_per_min": 12},
        {"name": "🧘 Yoga", "duration": max(15, calories // 4), "calories_per_min": 4},
        {"name": "🏊 Swimming", "duration": max(10, calories // 8), "calories_per_min": 8},
        {"name": "🤸 Jump Rope", "duration": max(8, calories // 12), "calories_per_min": 12}
    ]
    
    return exercises

# Test the functions if this file is run directly
if __name__ == "__main__":
    # Test with a sample food
    test_food = "Chapati"
    result = analyze_food_text(test_food)
    
    print(f"Test Analysis for: {test_food}")
    print(f"Calories: {result['calories']}")
    print(f"Protein: {result['protein']}g")
    print(f"Carbs: {result['carbs']}g")
    print(f"Fats: {result['fats']}g")
    print(f"Insight: {result['insight']}")
    
    # Test exercise suggestions
    exercises = get_exercise_suggestions(result['calories'])
    print(f"\nExercise to burn {result['calories']} calories:")
    for ex in exercises:
        print(f"  {ex['name']}: {ex['duration']} minutes")