import google.generativeai as genai
import os

# Your API key
API_KEY = os.getenv("AIzaSyC-O7lQBS27JHP9zHaOCD20LmwzeW0QmwA") or "AIzaSyC-O7lQBS27JHP9zHaOCD20LmwzeW0QmwA"  # Replace with your key

try:
    # Configure
    genai.configure(api_key=API_KEY)
    print("✅ Connected to Gemini API\n")
    
    # List all available models
    print("📋 AVAILABLE MODELS:")
    print("=" * 60)
    
    models = genai.list_models()
    gemini_models = []
    
    for model in models:
        if 'gemini' in model.name.lower():
            gemini_models.append(model)
            # Check which features each model supports
            print(f"Model: {model.name}")
            print(f"  Display Name: {model.display_name}")
            print(f"  Description: {model.description}")
            print(f"  Supports Vision: {'✅' if 'generateContent' in model.supported_generation_methods and hasattr(model, 'input_token_limit') else '❌'}")
            print(f"  Input Tokens: {getattr(model, 'input_token_limit', 'N/A')}")
            print(f"  Output Tokens: {getattr(model, 'output_token_limit', 'N/A')}")
            print("-" * 40)
    
    print(f"\n🎯 Total Gemini models found: {len(gemini_models)}")
    
    # Test which ones work with vision
    print("\n🧪 TESTING VISION MODELS:")
    print("=" * 60)
    
    vision_test_models = [
        "gemini-1.5-flash",  # Most likely to work
        "gemini-1.5-pro",    # Alternative
        "gemini-2.0-flash",  # Newer but might have quota
        "models/gemini-1.5-pro",  # Full path version
    ]
    
    for model_name in vision_test_models:
        try:
            print(f"\nTesting: {model_name}")
            model = genai.GenerativeModel(model_name)
            # Try a simple text generation first
            response = model.generate_content("Say 'test'")
            print(f"  Text test: ✅ '{response.text[:50]}...'")
            
            # You can add image test here if you want
            # print("  Vision capability: Checking...")
            
        except Exception as e:
            print(f"  ❌ Failed: {str(e)[:80]}...")
    
except Exception as e:
    print(f"❌ Setup error: {e}")
