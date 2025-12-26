# firebase_service.py
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import json

def init_firebase():
    """Initialize Firebase with service account"""
    try:
        cred = credentials.Certificate("firebase-service-account.json")
        firebase_admin.initialize_app(cred)
        return True
    except:
        # For testing, use mock data
        return False

def save_user_data(user_id, name, age, email):
    """Save user profile to Firestore"""
    if not init_firebase():
        return {"status": "demo", "message": "Using demo mode"}
    
    db = firestore.client()
    user_ref = db.collection('users').document(user_id)
    
    user_data = {
        'name': name,
        'age': age,
        'email': email,
        'created_at': datetime.now(),
        'daily_goal': {
            'calories': 2000,
            'protein': 50,
            'carbs': 250,
            'fats': 65
        }
    }
    
    user_ref.set(user_data)
    return {"status": "success", "user_id": user_id}

def save_food_log(user_id, food_data):
    """Save food intake to Firestore"""
    if not init_firebase():
        return {"status": "demo", "data": food_data}
    
    db = firestore.client()
    today = datetime.now().strftime("%Y-%m-%d")
    
    log_ref = db.collection('users').document(user_id)\
                .collection('daily_logs').document(today)
    
    # Get existing logs or create new
    existing = log_ref.get()
    if existing.exists:
        logs = existing.to_dict().get('foods', [])
    else:
        logs = []
    
    logs.append({
        **food_data,
        'timestamp': datetime.now()
    })
    
    log_ref.set({'foods': logs}, merge=True)
    
    # Update daily totals
    update_daily_totals(user_id, food_data)
    
    return {"status": "success"}

def update_daily_totals(user_id, food_data):
    """Update daily nutrition totals"""
    db = firestore.client()
    today = datetime.now().strftime("%Y-%m-%d")
    
    totals_ref = db.collection('users').document(user_id)\
                   .collection('daily_totals').document(today)
    
    existing = totals_ref.get()
    if existing.exists:
        current = existing.to_dict()
    else:
        current = {'calories': 0, 'protein': 0, 'carbs': 0, 'fats': 0}
    
    new_totals = {
        'calories': current.get('calories', 0) + food_data.get('calories', 0),
        'protein': current.get('protein', 0) + food_data.get('protein', 0),
        'carbs': current.get('carbs', 0) + food_data.get('carbs', 0),
        'fats': current.get('fats', 0) + food_data.get('fats', 0)
    }
    
    totals_ref.set(new_totals)
    