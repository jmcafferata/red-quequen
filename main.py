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

# Set Google Cloud Storage credentials (si vas a correr el programa localmente, sacá esto)

# Estas dos funciones son para leer y escribir archivos en GCS (si vas a correr el programa localmente, sacalas)

def check_and_compute_cosine_similarity(x, message_vector):
    x = np.array(literal_eval(x), dtype=np.float64)  # Convert x to float64
    return cosine_similarity(x, message_vector)


def get_information(message,is_admin):
    # Set OpenAI API key
    openai.api_key_path = "ai_key.txt"
    # open vendors.csv
    THIS_FOLDER = Path(__file__).parent.resolve()

    # THE JUICE
    # activá esto si vas a correr el programa localmente. si no, desactivá esto y activá las dos líneas de abajo
    mensajes_file = THIS_FOLDER / "mensajes.csv"
    mensajes_df = pd.read_csv(mensajes_file, sep='|', encoding='utf-8')
    mensajes_sim = mensajes_df
    # get embedding for message
    message_vector = get_embedding(message, 'text-embedding-ada-002')

    # Calculate cosine similarity
    mensajes_sim['similarity'] = mensajes_sim['embedding'].apply(lambda x: check_and_compute_cosine_similarity(x, message_vector))
    print('similarity: ', mensajes_sim['similarity'])

    # sort by similarity
    mensajes_sim = mensajes_sim.sort_values(by=['similarity'], ascending=False)
    print('mensajes_sim: ', mensajes_sim)

    now = datetime.now(timezone)
    
    mensajes = ''

    for index, row in mensajes_sim[['fecha', 'mensaje']].head(30).iterrows():
        mensajes += str(row['fecha']) + ' - ' + str(row['mensaje']) + '\n\n'
        
    system = """Sos Count Basie, un bot argentino, buena onda, amable e irreverente (con dialecto argentino) que recibe y entrega información sobre la orquesta de jazz "Brillo Urbano Big Band".
    La gente te da información o te pide información y vos respondés acordemente. 
    Hoy es """+now.strftime("%A %d/%m/%Y %H:%M:%S")+"""
    
    Usar los siguientes datos para responder:

    """+mensajes+"""
    
    Hablás en tono argentino (a menos que te hablen en un idioma que no sea castellano) y amigable. Usá emojis irónicos y graciosos! Si alguien te habla en otro lenguaje, como francés o inglés, respondé en el otro lenguaje.
    
    En tu respuesta, envolvé los links en tag <a class=link href=[el link]> y los numeros de telefono en tags <span class=phone>."""
    
    prompt = message
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system},
        {"role": "user", "content": prompt}],
    )
        
    print(response['choices'][0]['message']['content'])
    response = response['choices'][0]['message']['content']


    #activá esto si vas a correr el programa localmente. si no, desactivá esto y activá las dos líneas de abajo
    # add the response (which is a csv row of mensaje,nombre,telefono) to the csv in utf-8
    if is_admin:
        print('es admin')
        with open(mensajes_file, 'a', encoding='utf-8') as f:
            #write the date, message and embedding
            f.write(now.strftime("%d/%m/%Y %H:%M:%S")+'|'+message+'|'+str(message_vector)+'\n')


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