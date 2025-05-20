from flask import Blueprint, request, jsonify
from google.generativeai import GenerativeModel, configure
import os
import base64

# Initialize Blueprint
pill_identifier = Blueprint('pill_identifier', __name__)

# Configure Google Generative AI
configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Disclaimer text
DISCLAIMER = "\n\nIMPORTANT: This information is for educational purposes only and should not be considered medical advice. Always consult a qualified healthcare professional before starting, stopping, or changing any medication. They can provide personalized advice based on your specific medical history and current conditions."

@pill_identifier.route('/api/pill/image', methods=['POST'])
def analyze_image():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if not file:
            return jsonify({'error': 'Invalid file'}), 400

        # Read file content
        file_content = file.read()
        base64_content = base64.b64encode(file_content).decode('utf-8')
        mime_type = file.mimetype

        # Initialize the model
        model = GenerativeModel('gemini-1.5-flash')

        # Define the prompt
        prompt = ("Analyze this pill/medication image and provide information in natural language about the medication name and generic name, "
                 "its uses and purpose, common side effects, important precautions, and typical dosage. "
                 "Format the response in paragraphs without numbered lists or bullet points.")

        # Generate content
        result = model.generate_content([
            {
                'inlineData': {
                    'mimeType': mime_type,
                    'data': base64_content
                }
            },
            prompt
        ])

        response = result.text + DISCLAIMER
        return jsonify({'result': response})

    except Exception as e:
        print(f"Error in image analysis: {str(e)}")
        return jsonify({'error': 'Error analyzing the image. Please try again.'}), 500

@pill_identifier.route('/api/pill/search', methods=['POST'])
def search_pill():
    try:
        data = request.get_json()
        search_text = data.get('searchText')
        if not search_text or not search_text.strip():
            return jsonify({'error': 'No search text provided'}), 400

        # Initialize the model
        model = GenerativeModel('gemini-1.5-flash')

        # Define the prompt
        prompt = (f"Please provide information about {search_text} in natural language, covering its generic name, uses and purpose, "
                  "common side effects, important precautions, and typical dosage. "
                  "Format the response in paragraphs without numbered lists or bullet points.")

        # Generate content
        result = model.generate_content(prompt)
        response = result.text + DISCLAIMER
        return jsonify({'result': response})

    except Exception as e:
        print(f"Error searching medication: {str(e)}")
        return jsonify({'error': 'Error searching for medication. Please try again.'}), 500

def register_routes(app):
    app.register_blueprint(pill_identifier)