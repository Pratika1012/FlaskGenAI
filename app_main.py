
from flask import Flask, render_template, request, after_this_request, session
from utils.dynamic_ocr import get_text_from_any_pdf, process_pdf
from werkzeug.utils import secure_filename
from utils.single_case_summary import extract_text_from_pdf, chat_interface_single, chat_interface_user_single
from utils.multiple_case_summary import extract_text_from_pdf, chat_interface_multiple
from utils.translate_ocr import translate_and_process_pdf
import os
import openai
import json
app = Flask(__name__)
app.secret_key = "ninu_gen_ai"

#edit here
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')

# Ensure the 'uploads' directory exists
upload_folder = os.path.join(app.root_path, 'static/uploads')
os.makedirs(upload_folder, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    option = request.form['option']
    if 'file' in request.files:
        file = request.files['file']
        # Process the file upload form here
        # Use Flask's built-in temporary file handling
        filename = secure_filename(file.filename)
        temp_filename = os.path.join(upload_folder, filename)
        file.save(temp_filename)


    # Retrieve API key from the form data
    api_key = request.form['api_key']

    # Update OpenAI API key
    openai.api_key = api_key

    #Dynamic OCR
    if option == 'Dynamic OCR':
        pdf_text = get_text_from_any_pdf(temp_filename)
        # Process PDF text
        processed_json = process_pdf(temp_filename)
        formatted_dynamic_ocr = json.dumps(processed_json, indent=4)
        return render_template('index.html', dynamic_ocr=formatted_dynamic_ocr)

    #Single_Case_Summary
    elif option == 'Single Case Summary':
        extracted_text = extract_text_from_pdf(temp_filename)
        session['extracted_text'] = extracted_text 
        chatbot_response = chat_interface_single(extracted_text)
        return render_template('index.html', chatbot_response_single=chatbot_response)
    
    #Translate_OCR
    elif option == 'Translate OCR':
        translated_json = translate_and_process_pdf(temp_filename)
        return render_template('index.html', translated_ocr=translated_json)
    
    #Multiple_Case_Summary
    elif option == 'Multiple Case Summary':
        extracted_text = extract_text_from_pdf(temp_filename)
        chatbot_response = chat_interface_multiple(extracted_text)
        return render_template('index.html', chatbot_response_multiple=chatbot_response)

@app.route('/user_input', methods=['POST'])
def user_input():
    option = request.form['option']
    user_input3 = request.form.get('user_input3')

    api_key = request.form['api_key']

    # Update OpenAI API key
    openai.api_key = api_key

    if option == 'Single Case Summary':
        extracted_text = session.get('extracted_text')
        chatbot_response = chat_interface_user_single(extracted_text, user_input3)
        return render_template('index.html', chatbot_response_single=chatbot_response)
    

if __name__ == '__main__':
    app.run(debug=True)