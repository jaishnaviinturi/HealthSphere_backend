import fitz  
import google.generativeai as gemini
import json
from flask import Flask, request, jsonify
from flask_cors import CORS  
from werkzeug.utils import secure_filename
import os
import pytesseract
from PIL import Image
import re
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app) 

tesseract_cmd = os.getenv("TESSERACT_CMD")
if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

gemini.configure(api_key=os.getenv("GEMINI_API_KEY"))

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_image(image_path):
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        raise Exception(f"OCR Error: {str(e)}")

def analyze_medical_report(text):
    prompt = f"""
    You are a highly advanced medical analysis AI. Analyze the following medical report and provide a detailed summary, including:
    - Identified medical metrics (e.g., Blood Glucose, Cholesterol, CBC, Platelets, Blood Pressure, Oxygen Level, Hemoglobin, etc.)
    - Comparison with standard ranges (for all metrics, using reliable medical sources like UMLS, SNOMED CT).
    - Any abnormal findings with recommendations for further actions.
    - If specific ranges are not provided, use general medical knowledge to determine the normal ranges.

    Medical Report:
    {text}

    Provide the analysis in a structured JSON format with the following keys:
    - Metrics
    - Analysis
    - Recommendations
    """
    
    model = gemini.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(
        prompt,
        generation_config={
            "max_output_tokens": 3000,
            "temperature": 0.2
        }
    )

    response_text = response.text.strip()
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        cleaned_json = json_match.group(0)
        try:
            return json.loads(cleaned_json) 
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse cleaned JSON: {str(e)}. Raw response: {cleaned_json}")
    else:
        raise Exception(f"No valid JSON found in response: {response_text}")

@app.route('/analyze-report', methods=['POST'])
def analyze_report():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            temp_path = os.path.join('uploads', filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(temp_path)
            
            file_extension = filename.rsplit('.', 1)[1].lower()
            if file_extension == 'pdf':
                extracted_text = extract_text_from_pdf(temp_path)
            else:
                extracted_text = extract_text_from_image(temp_path)
            
            analysis = analyze_medical_report(extracted_text)
            os.remove(temp_path)
            
            return jsonify({
                'analysis': analysis, 
                'source_type': 'pdf' if file_extension == 'pdf' else 'image'
            }), 200
                
        else:
            return jsonify({'error': 'Invalid file type. Please upload a PDF or image (PNG/JPG/JPEG)'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)