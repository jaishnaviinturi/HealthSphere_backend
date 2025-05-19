import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app) 

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash') 

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        age = data.get('age')
        gender = data.get('gender')
        height = data.get('height')
        weight = data.get('weight')
        activity_level = data.get('activityLevel')
        fitness_level = data.get('fitnessLevel')
        primary_goal = data.get('primaryGoal')
        dietary_preference = data.get('dietaryPreference') or 'none'
        plan_type = data.get('planType', 'diet') 

        required_fields = ['age', 'gender', 'height', 'weight', 'activityLevel', 'fitnessLevel', 'primaryGoal']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400

        bmi = weight / ((height / 100) ** 2)  

        if plan_type == 'diet':
            prompt = f"""
            You are a fitness and nutrition expert. Generate a personalized nutrition plan for a {age}-year-old {gender} who is {height} cm tall, weighs {weight} kg, has a BMI of {bmi:.1f}, an activity level of "{activity_level}", a fitness level of {fitness_level}/5, a primary goal of "{primary_goal}", and a dietary preference of "{dietary_preference}". 

            Provide the following sections in plain text (do not use markdown or special characters like ** or * for formatting):
            Overview: A brief summary of the user's profile and recommendations (e.g., caloric intake, focus areas).
            Sample Meal Plan: A detailed daily meal plan with breakfast, mid-morning snack, lunch, afternoon snack, dinner, and an optional evening snack.
            Water Intake: Recommended daily water intake.
            Pro Tips: 3-5 actionable tips to help achieve the goal.

            Format the response with clear section headers (e.g., "Overview", "Sample Meal Plan") separated by newlines.
            """
        else:  
            prompt = f"""
            You are a fitness and nutrition expert. Generate a personalized workout plan for a {age}-year-old {gender} who is {height} cm tall, weighs {weight} kg, has a BMI of {bmi:.1f}, an activity level of "{activity_level}", a fitness level of {fitness_level}/5, and a primary goal of "{primary_goal}". 

            Provide the following sections in plain text (do not use markdown or special characters like ** or * for formatting):
            Overview: A brief summary of the user's fitness profile and workout recommendations.
            Weekly Workout Plan: A detailed weekly workout plan with exercises for each day (e.g., Monday: Cardio, Tuesday: Strength Training).
            Warm-Up and Cool-Down: Suggested warm-up and cool-down routines.
            Pro Tips: 3-5 actionable tips to help achieve the fitness goal.

            Format the response with clear section headers (e.g., "Overview", "Weekly Workout Plan") separated by newlines.
            """

        response = model.generate_content(prompt)
        plan = response.text 

        return jsonify({'plan': plan})

    except Exception as e:
        return jsonify({'error': f'Failed to generate plan: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)