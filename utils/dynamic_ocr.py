
import openai
import json
import pytesseract
from pdf2image import convert_from_path
from pytesseract import image_to_string

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def convert_pdf_to_img(pdf_file):
    return convert_from_path(pdf_file, poppler_path=r'C:\Program Files\poppler-23.07.0\Library\bin')

def convert_image_to_text(file):  
    text = image_to_string(file)
    return text

def get_text_from_any_pdf(pdf_file):
    images = convert_pdf_to_img(pdf_file)
    final_text = ""
    for pg, img in enumerate(images):
        final_text += convert_image_to_text(img)
    return final_text

def get_completion(prompt, model="gpt-3.5-turbo-16k"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def process_pdf(uploaded_file_name):
    ext_text = get_text_from_any_pdf(uploaded_file_name)

    input_text = f"""
Your task is to convert the data into json format
Format the json proper key value pair. 

If the data contains any boxes, do create the proper check boxes for someone to tick or untick it.' 

Entire json format should be editable as this is a pdf editable form.
Context: {ext_text}
"""

    # Assuming you have a function get_completion that gets a completion based on input text
    response_text = get_completion(input_text)
    json_data = json.loads(response_text)
    
    return json_data






