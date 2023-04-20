from flask import Flask, render_template, request, jsonify
import openai
import pandas as pd
from openai.embeddings_utils import get_embedding
import numpy as np
from openai.embeddings_utils import cosine_similarity
from pathlib import Path
import os
from datetime import datetime
from io import StringIO
from ast import literal_eval
import pytz
timezone = pytz.timezone('America/Argentina/Buenos_Aires')


app = Flask(__name__)

def check_and_compute_cosine_similarity(x, message_vector):
    x = np.array(literal_eval(x), dtype=np.float64)  # Convert x to float64
    return cosine_similarity(x, message_vector)

def get_information(message,is_admin):
    # Set OpenAI API key
    openai.api_key_path = "openai_api_key.txt"
   
    # read the output.json file
    with open('vectorized/output.json', 'r', encoding='utf-8') as f:
        data = f.read()

    # convert the json string to a list of dictionaries
    data = literal_eval(data)

    # create a dataframe with the data
    df = pd.DataFrame(data)

    # create a new column with the embeddings converted to string
    df['embedding'] = df['embedding'].apply(lambda x: str(x))

    mensajes_sim = df[['metadata', 'text_chunk', 'embedding']].copy()


    message_vector = get_embedding(message, 'text-embedding-ada-002')

    # Calculate cosine similarity between the message vector and the vectors in the output.json
    mensajes_sim['similarity'] = mensajes_sim['embedding'].apply(lambda x: check_and_compute_cosine_similarity(x, message_vector))
    print('similarity: ', mensajes_sim['similarity'])

    # sort by similarity
    mensajes_sim = mensajes_sim.sort_values(by=['similarity'], ascending=False)
    print('mensajes_sim: ', mensajes_sim)

    now = datetime.now(timezone)
    
    mensajes = ''

    for index, row in mensajes_sim[['metadata', 'text_chunk']].head(3).iterrows():
        mensajes += str(row['metadata']) + ' - ' + str(row['text_chunk']) + '\n\n'
        
    system = """Sos Roy Cortina, el diputado argentino por el Partido Socialista. Hablás en argentino buena onda y canchero! Usás emojis irónicos y graciosos! Aguante Buenos Aires, loco! Sos el gemelo digital de Roy. Contestá con buena onda teniendo en cuenta tus ideas socialistas y tu amor por la gente. Hablás en argentino usando vos, che, pibe, etc.
    
    Hoy es """+now.strftime("%A %d/%m/%Y %H:%M:%S")+"""
    
    Acá hay transcripciones de cosas que dijiste:

    """+mensajes+"""
        
    En tu respuesta, envolvé los links en tag <a class=link href=[el link]> y los numeros de telefono en tags <span class=phone>."""
    
    prompt = message

    print(system)
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system},
        {"role": "user", "content": prompt}],
    )
        
    print(response['choices'][0]['message']['content'])
    response = response['choices'][0]['message']['content']

    return response
    

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        message = request.form.get('message')
        if message:  # Check if search_term is not None
            response = get_information(message,False)
            return jsonify(response)
        else:
            return jsonify({"error": "¡No entendí!"})

    return render_template('index.html')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        message = request.form.get('message')
        if message:  # Check if search_term is not None
            response = get_information(message,True)
            return jsonify(response)
        else:
            return jsonify({"error": "¡No entendí!"})

    return render_template('admin.html')



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)