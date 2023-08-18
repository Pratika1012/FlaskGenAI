# translate_utils.py
import openai
import PyPDF2
import json



def get_completion(prompt, model="gpt-3.5-turbo-16k"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,  # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def translate_and_process_pdf(uploaded_file_name):

    pdfFileObject = open(uploaded_file_name, 'rb')
    pdfReader = PyPDF2.PdfReader(pdfFileObject)
    text = []
    for i in range(0, len(pdfReader.pages)):
        pageObj = pdfReader.pages[i].extract_text()
        pageObj = pageObj.replace('\t\r', '')
        pageObj = pageObj.replace('\xa0', '')
        text.append(pageObj)

    prompt = f"""UserinputData in japanese converted to english"
    {text}"""
    try:
        response = get_completion(prompt)
    except:
        response = get_completion(prompt)

    prompt1 = f"""
    Your task is to convert the data into json format
    Format the json proper key value pair.
    Check if the details are related to each other for example someone's details,
    if the data contains any boxes, do create the proper check boxes for someone to tick or untick it.'
    which can include name, date of birth, age, gender, weight, height etc then those should be included as a sub dict
    Entire json format should be editable as this is a pdf editable form
    
    ```{response}``
    """
    response1 = get_completion(prompt1)
    json_data1 = json.loads(response1)
    
    return json_data1
