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
import config
timezone = pytz.timezone('America/Argentina/Buenos_Aires')


app = Flask(__name__)


def check_and_compute_cosine_similarity(x, message_vector):
    x = np.array(literal_eval(x), dtype=np.float64)  # Convert x to float64
    return cosine_similarity(x, message_vector)


def get_information(message,isadmin):

    now = datetime.now(timezone)

    # Set OpenAI API key
    openai.api_key_path = "ai_key.txt"
    THIS_FOLDER = Path(__file__).parent.resolve()

    mensajes_file = THIS_FOLDER / "mensajes.csv"
    mensajes_df = pd.read_csv(mensajes_file, sep='|', encoding='utf-8')
    mensajes_sim = mensajes_df

    message_vector = get_embedding(message, 'text-embedding-ada-002')
    
    with open(mensajes_file, 'a', encoding='utf-8') as f:
    #write the date, message and embedding
        f.write(now.strftime("%d/%m/%Y %H:%M:%S")+'|'+message+'|'+str(message_vector)+'\n')

    # Calculate cosine similarity
    mensajes_sim['similarity'] = mensajes_sim['embedding'].apply(lambda x: check_and_compute_cosine_similarity(x, message_vector))
    print('similarity: ', mensajes_sim['similarity'])

    # sort by similarity
    mensajes_sim = mensajes_sim.sort_values(by=['similarity'], ascending=False)
    print('mensajes_sim: ', mensajes_sim)

    
    mensajes = ''

    for index, row in mensajes_sim[['fecha', 'mensaje']].head(30).iterrows():
        mensajes += str(row['fecha']) + ' - ' + str(row['mensaje']) + '\n\n'
        
    system = config.personalidad + """
    
    Hoy es """+now.strftime("%A %d/%m/%Y %H:%M:%S")+ """Mi mensaje para vos es el siguiente:

"""+message+"""

Si el mensaje suena como una consulta (la gente lo puede usar como si fuera una query de Google, ejemplo "panaderia abierta"), responder con información clara, precisa y que ayude usando la siguiente información previamente ingresada. Cada mensaje tiene la fecha y hora en que la persona lo envió, y eso también es útil para informar.

"""+mensajes+"""

Por favor, las fechas que estén en un formato humano (como "hoy" o "ayer"). Reservar el uso de números para precios y teléfonos.  En tu respuesta, envolvé los links en tag <a class=link href=[el link]> y los numeros de telefono en tags <span class=phone>."""


    prompt = message
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
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