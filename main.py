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
    # oferta_file = THIS_FOLDER / "oferta.csv"
    # demanda_file = THIS_FOLDER / "demanda.csv"
    # oferta_df = pd.read_csv(oferta_file, sep='|', encoding='utf-8')
    # oferta_sim = oferta_df

    # desactivá esto si vas a correr el programa localmente. si no, activá esto y desactivá las dos líneas de arriba
    # Read CSV from GCS
    oferta_df = read_csv_from_gcs("oferta.csv")
    oferta_sim = oferta_df
    demanda_df = read_csv_from_gcs("demanda.csv")   

    # get embedding for message
    message_vector = get_embedding(message, 'text-embedding-ada-002')
    print('message_vector: ', message_vector)
    # parse embedding column ////// update: son todos lists, no hace falta
    # oferta_sim['embedding'] = oferta_sim['embedding'].apply(lambda x: x[1:-1].strip('()').split(','))
    
    # Calculate cosine similarity
    oferta_sim['similarity'] = oferta_sim['embedding'].apply(lambda x: check_and_compute_cosine_similarity(x, message_vector))
    print('similarity: ', oferta_sim['similarity'])

    # sort by similarity
    oferta_sim = oferta_sim.sort_values(by=['similarity'], ascending=False)
    print('oferta_sim: ', oferta_sim)

    now = datetime.now()

    prompt = 'Sos un bot argentino, buena onda y amable (con dialecto argentino) que tiene información sobre el pueblo de Quequén. La gente te da información o te pide información y vos respondés acordemente. Hoy es '+now.strftime("%d/%m/%Y %H:%M:%S")+'.\nMi mensaje para vos es el siguiente.\n\n"'+message+'"\n\nSi el mensaje suena como un ingreso de información, que la respuesta sea una versión resumida, concreta y útil de la información.\n\nSi el mensaje suena como una consulta (la gente lo puede usar como si fuera una query de Google, ejemplo "panaderia abierta"), responder con información clara, precisa y que ayude usando la siguiente información previamente ingresada:\n\n'+oferta_sim[['fecha','mensaje']].head(20).to_string(index=False)+'\n\nAdemás, si el mensaje es un ingreso, que tu respuesta empiece con la palabra "INGRESO\n" (con la nueva línea) y si el mensaje es una consulta, que tu respuesta empiece con la palabra "CONSULTA\n" (con la nueva línea). Hablás en tono argentino y amigable, un poco revolucionario. Te divierte muchoque Quequén comience a ser libre finalmente de toda autoridad. Por favor, las fechas que estén en un formato humano (como "hoy" o "ayer"). Reservar el uso de números para precios y teléfonos."'
    print(prompt)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
        {"role": "user", "content": prompt}],
    )
    

    # if the response starts with "INGRESO", o sea OFERTA
    if response['choices'][0]['message']['content'].startswith('INGRESO'):
        # get the response after it finds '\n'
        print(response['choices'][0]['message']['content'])
        response = response['choices'][0]['message']['content'].split('\n')[1]

        #activá esto si vas a correr el programa localmente. si no, desactivá esto y activá las dos líneas de abajo
        # add the response (which is a csv row of mensaje,nombre,telefono) to the csv in utf-8
        # with open(oferta_file, 'a', encoding='utf-8') as f:
        #     # write date, message, response, and message_vector to csv
        #     f.write(f"{now.strftime('%Y-%m-%d %H:%M:%S')}|{message}|{message_vector}\n")            
            
        # desactivá esto si vas a correr el programa localmente. si no, activá esto y desactivá las dos líneas de arriba
        # add the response (which is a csv row of mensaje,nombre,telefono) to the csv in utf-8
        oferta_df = oferta_df.append({'fecha': now.strftime("%d/%m/%Y %H:%M:%S"), 'mensaje': message, 'embedding': str(message_vector)}, ignore_index=True)
        write_csv_to_gcs(oferta_df, "oferta.csv")

        # return the response
        return "¡Se agregó tu información al sistema! Cualquier consulta hablá conmigo."
    
    # if the response starts with "CONSULTA", o sea DEMANDA
    elif response['choices'][0]['message']['content'].startswith('CONSULTA'):
        # get the response after it finds '\n'
        print(response['choices'][0]['message']['content'])
        response = response['choices'][0]['message']['content'].split('\n')[1]


        #activá esto si vas a correr el programa localmente. si no, desactivá esto y activá las dos líneas de abajo
        # add the response (which is a csv row of mensaje,nombre,telefono) to the csv in utf-8
        # with open(demanda_file, 'a', encoding='utf-8') as f:
        #     #write the date, message and embedding
        #     f.write(now.strftime("%d/%m/%Y %H:%M:%S")+'|'+message+'|'+str(message_vector)+'\n')

        # desactivá esto si vas a correr el programa localmente. si no, activá esto y desactivá las dos líneas de arriba
        # use pandas.concat to add the response (which is a csv row of mensaje,nombre,telefono) to the csv in utf-8
        demanda_df = demanda_df.append({'fecha': now.strftime("%d/%m/%Y %H:%M:%S"), 'mensaje': message, 'embedding': str(message_vector)}, ignore_index=True)
        write_csv_to_gcs(demanda_df, "demanda.csv")

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