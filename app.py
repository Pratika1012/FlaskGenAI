from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


import pytesseract
import pdfplumber
from pdf2image import convert_from_path
import openai
import pandas as pd
import fitz

#setting up the APIkey for OpenAI ChatGPT
openai.api_key  = "your api key"


#creating the function to get the response from ChatGPT API using prompts
def get_completion(prompt, model="gpt-3.5-turbo-16k"):
  messages = [{"role": "user", "content": prompt}]
  response = openai.ChatCompletion.create(
     model=model,
     messages=messages,
    
     temperature=0.7,
#      temperature=0, # this is the degree of randomness of the model's output
  )
  return response.choices[0].message["content"]

# Function to convert PDF to Images (same as before)
def convert_pdf_to_img(pdf_file):
    images = convert_from_path(pdf_file, poppler_path=r'C://Program Files//poppler-23.07.0//Library//bin')
    return images

# Function to extract text from an Image (same as before)
def extract_text_from_image(image):
    text = pytesseract.image_to_string(image)
    return text

# Function to get text from all pages of a PDF (same as before)
def get_text_from_any_pdf(pdf_file):
    images = convert_pdf_to_img(pdf_file)
    final_text = ""
    for pg, img in enumerate(images):
        final_text += extract_text_from_image(img)
    return final_text

# Function to translate the text to English
def translate_to_english(final_text):
    prompt = f"""
        UserInput Data is in spanish convert to english
        
        Context: {final_text}
        
        Answer: 
    """
    response = get_completion(prompt)
    return response

@app.route('/translate_pdf', methods=['POST'])
def translate_pdf():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['pdf_file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file:
        ocr_text = get_text_from_any_pdf(file)
        translated_text = translate_to_english(ocr_text)
        return jsonify({'translated_text': translated_text})

# Function to process the question using GPT-3.5
def chat_with_gpt(question, pdf_text):
    # Set up the message with user question and PDF text as context
    messages = [{"role": "user", "content": question}, {"role": "assistant", "content": pdf_text}]
    
    # Get the response from GPT-3.5
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=messages,
        temperature=0.7,
    )
    
    # Extract the assistant's reply from the API response
    assistant_reply = response['choices'][0]['message']['content']
    return assistant_reply

def extract_text_from_pdf(pdf_file):
    text = ""
    with fitz.open(stream=pdf_file.read(), filetype="pdf") as pdf_document:
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
    return text


@app.route('/chat_gpt', methods=['POST'])
def chat_gpt():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'No file part'})
    pdf_file = request.files['pdf_file']
    if pdf_file.filename == '':
        return jsonify({'error': 'No selected file'})
    question = request.form['question']
    if not question:
        return jsonify({'error': 'No question provided'})
    if pdf_file:
        pdf_text = extract_text_from_pdf(pdf_file)
        response = chat_with_gpt(question, pdf_text)
        return jsonify({'response': response})
    

@app.route('/data_processing', methods=['POST'])
def data_processing():
    # Implement data processing logic here
    # For simplicity, let's assume it returns a placeholder response
    return jsonify({'response': 'Data processing is in progress.'})


if __name__ == '__main__':
    app.run(debug = True)




# <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
# <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">