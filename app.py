from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from utils.dynamic_ocr import process_pdf
from utils.single_case_summary import extract_text_from_pdf_single, chat_interface_single
from utils.multiple_case_summary import extract_text_from_pdf_multiple, chat_interface_multiple
from utils.translate_ocr import translate_and_process_pdf
import os
import openai
import json
from apscheduler.schedulers.background import BackgroundScheduler
import glob
import atexit
import time
from config import IP_ADDRESS, KEY_FILE, SUBDOMAIN

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
app.secret_key = b"gen_ai"

# Ensure the 'uploads' directory exists
upload_folder = os.path.join(app.root_path, 'static/uploads')
os.makedirs(upload_folder, exist_ok=True)

scheduler = BackgroundScheduler()
scheduler.start()

def cleanup_upload_folder():
    files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], "*.*"))
    current_time = time.time()
    
    for file in files:
        try:
            file_creation_time = os.path.getctime(file)
            if current_time - file_creation_time > 24 * 60 * 60:  # Delete files older than 24 hours
                os.remove(file)  # Delete the file
        except Exception as e:
            print(f"Error deleting file: {e}")

# Add the cleanup function to the scheduler to run every hour
scheduler.add_job(cleanup_upload_folder, "interval", hours=1)

def delete_uploaded_file(filename):
    try:
        os.remove(filename)  # Delete the uploaded file
    except Exception as e:
        print(f"Error deleting file: {e}")

def validate_option(option):
    valid_options = ['Dynamic OCR', 'Single Case Summary', 'Translate OCR', 'Multiple Case Summary']
    return option in valid_options

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    global filename
    option = request.form.get('option')
    
    # Initialize the filename variable
    filename = None

    if 'file' in request.files:
        file = request.files['file']
        if file:
            filename = os.path.join(upload_folder, secure_filename(file.filename))
            try:
                file.save(filename)
                atexit.register(delete_uploaded_file, filename)
            except Exception as e:
                return f"Error saving file: {e}", 500
        else:
            return "No file uploaded", 400

    api_key = request.form.get('api_key')
    if not api_key:
        return "API key missing", 400

    if not validate_option(option):
        return "Invalid option selected", 400

    # Update OpenAI API key
    openai.api_key = api_key

    try:
        if option == 'Dynamic OCR':
            processed_json = process_pdf(filename)
            formatted_dynamic_ocr = json.dumps(processed_json, indent=4)
            return render_template('index.html', dynamic_ocr=formatted_dynamic_ocr)

        elif option == 'Single Case Summary':
            extracted_text = extract_text_from_pdf_single(filename)
            chatbot_response = chat_interface_single(extracted_text)
            return render_template('index.html', chatbot_response_single=chatbot_response)

        elif option == 'Translate OCR':
            translated_json = translate_and_process_pdf(filename)
            formatted_translated_json = json.dumps(translated_json, indent=4)
            return render_template('index.html', translated_ocr=formatted_translated_json)

        elif option == 'Multiple Case Summary':
            extracted_text = extract_text_from_pdf_multiple(filename)
            chatbot_response = chat_interface_multiple(extracted_text)
            return render_template('index.html', chatbot_response_multiple=chatbot_response)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
