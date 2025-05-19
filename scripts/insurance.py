import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")  
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

app = Flask(__name__)
CORS(app)  

def get_health_insurance_recommendations(user_profile):
    """
    Generate personalized health insurance recommendations.
    
    Args:
        user_profile (dict): Dictionary containing user details (age, location, etc.)
    
    Returns:
        dict: Response with status and either the plans or an error message
    """
    required_fields = ["age", "location", "health_status", "smoker", "income_level", "family_status"]
    if not all(field in user_profile for field in required_fields):
        return {"status": "error", "message": "Missing required profile fields"}

    prompt = f"""
    You are a health insurance expert. Based on the following user profile, dynamically generate a list of 3 suitable health insurance plan options (e.g., HMO, PPO, High-Deductible with HSA) with descriptions tailored to the user’s needs:
    - Age: {user_profile['age']}
    - Location: {user_profile['location']}
    - Health Status: {user_profile['health_status']}
    - Smoker: {user_profile['smoker']}
    - Income Level: {user_profile['income_level']}
    - Family Status: {user_profile['family_status']}
    For each plan, provide:
    1. Plan type (e.g., HMO, PPO)
    2. A short description explaining why it suits the user
    Return the response as a structured list.
    """

    try:
        response = model.generate_content(prompt)
        dynamic_plans = response.text
        return {"status": "success", "plans": dynamic_plans}
    except Exception as e:
        return {"status": "error", "message": f"Error calling Gemini API: {str(e)}"}

@app.route('/api/health-insurance', methods=['POST'])
def health_insurance():
    """
    Flask endpoint to handle health insurance recommendation requests.
    
    Expects JSON payload with user profile data.
    Returns JSON response with recommendations or error.
    """
    user_profile = request.get_json()
    if not user_profile:
        return jsonify({"status": "error", "message": "No data provided"}), 400
    
    result = get_health_insurance_recommendations(user_profile)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)