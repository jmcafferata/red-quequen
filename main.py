from flask import Flask, render_template, request, jsonify
import openai
import pandas as pd
from openai.embeddings_utils import get_embedding
import numpy as np
from openai.embeddings_utils import cosine_similarity
from pathlib import Path
import os
from datetime import datetime
from google.cloud import storage
from io import StringIO
from ast import literal_eval
import pytz
timezone = pytz.timezone('America/Argentina/Buenos_Aires')


app = Flask(__name__)

# Set Google Cloud Storage credentials (si vas a correr el programa localmente, sacá esto)
GCS_CLIENT = storage.Client().from_service_account_json('key.json')
BUCKET = GCS_CLIENT.get_bucket("red-quequen.appspot.com")

# Estas dos funciones son para leer y escribir archivos en GCS (si vas a correr el programa localmente, sacalas)
def read_csv_from_gcs(file_name):
    blob = BUCKET.blob(file_name)
    csv_str = blob.download_as_string()
    return pd.read_csv(StringIO(csv_str.decode('utf-8')), sep='|', encoding='utf-8')
    
def write_csv_to_gcs(df, file_name):
    blob = BUCKET.blob(file_name)
    blob.upload_from_string(df.to_csv(sep='|', encoding='utf-8', index=False), 'text/csv')

def check_and_compute_cosine_similarity(x, message_vector):
    x = np.array(literal_eval(x), dtype=np.float64)  # Convert x to float64
    return cosine_similarity(x, message_vector)


def get_information(message):
    # Set OpenAI API key
    openai.api_key_path = "ai_key.txt"
    # open vendors.csv
    THIS_FOLDER = Path(__file__).parent.resolve()

    # activá esto si vas a correr el programa localmente. si no, desactivá esto y activá las dos líneas de abajo
    # mensajes_file = THIS_FOLDER / "mensajes.csv"
    # mensajes_df = pd.read_csv(mensajes_file, sep='|', encoding='utf-8')
    # mensajes_sim = mensajes_df

    # desactivá esto si vas a correr el programa localmente. si no, activá esto y desactivá las dos líneas de arriba
    # Read CSV from GCS
    mensajes_df = read_csv_from_gcs("mensajes.csv")
    mensajes_sim = mensajes_df

    # get embedding for message
    message_vector = get_embedding(message, 'text-embedding-ada-002')
    # parse embedding column ////// update: son todos lists, no hace falta
    # mensajes_sim['embedding'] = mensajes_sim['embedding'].apply(lambda x: x[1:-1].strip('()').split(','))
    
    # Calculate cosine similarity
    mensajes_sim['similarity'] = mensajes_sim['embedding'].apply(lambda x: check_and_compute_cosine_similarity(x, message_vector))
    print('similarity: ', mensajes_sim['similarity'])

    # sort by similarity
    mensajes_sim = mensajes_sim.sort_values(by=['similarity'], ascending=False)
    print('mensajes_sim: ', mensajes_sim)

    now = datetime.now(timezone)
    
    mensajes = 'Mensajes previos:\n\n'

    for index, row in mensajes_sim[['fecha', 'mensaje']].head(30).iterrows():
        mensajes += str(row['fecha']) + ' - ' + str(row['mensaje']) + '\n\n'
        

    prompt = 'Sos Red Quequén, un bot argentino, buena onda y amable (con dialecto argentino) que recibe y entrega información sobre el pueblo de Quequén. La gente te da información o te pide información y vos respondés acordemente. Hoy es '+now.strftime("%A %d/%m/%Y %H:%M:%S")+'.\nMi mensaje para vos es el siguiente.\n\n"'+message+'"Si el mensaje suena como una consulta (la gente lo puede usar como si fuera una query de Google, ejemplo "panaderia abierta"), responder con información clara, precisa y que ayude usando la siguiente información previamente ingresada. Cada mensaje tiene la fecha y hora en que la persona lo envió, y eso también es útil para informar.\n\n'+mensajes+'\n\nHablás en tono argentino (a menos que te hablen en un idioma que no sea castellano) y amigable, un poco revolucionario. Te divierte mucho que Quequén comience a ser libre finalmente de toda autoridad. Por favor, las fechas que estén en un formato humano (como "hoy" o "ayer"). Reservar el uso de números para precios y teléfonos. Recordale a la gente que agregue información útil para que Quequén prospere. Usá emojis irónicos y graciosos! Si alguien te habla en otro lenguaje, como francés o inglés, respondé en el otro lenguaje."'
    print(prompt)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
        {"role": "user", "content": prompt}],
    )
        
    print(response['choices'][0]['message']['content'])
    response = response['choices'][0]['message']['content']


    #activá esto si vas a correr el programa localmente. si no, desactivá esto y activá las dos líneas de abajo
    # add the response (which is a csv row of mensaje,nombre,telefono) to the csv in utf-8
    # with open(mensajes_file, 'a', encoding='utf-8') as f:
    #     #write the date, message and embedding
    #     f.write(now.strftime("%d/%m/%Y %H:%M:%S")+'|'+message+'|'+str(message_vector)+'\n')

    # desactivá esto si vas a correr el programa localmente. si no, activá esto y desactivá las dos líneas de arriba
    # use pandas.concat to add the response (which is a csv row of mensaje,nombre,telefono) to the csv in utf-8
    mensajes_df = mensajes_df.append({'fecha': now.strftime("%d/%m/%Y %H:%M:%S"), 'mensaje': message, 'embedding': str(message_vector)}, ignore_index=True)
    write_csv_to_gcs(mensajes_df, "mensajes.csv")

    return response
    

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        message = request.form.get('message')
        if message:  # Check if search_term is not None
            response = get_information(message)
            return jsonify(response)
        else:
            return jsonify({"error": "¡No entendí!"})

    return render_template('index.html')
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)