from flask import Flask, render_template, request, jsonify
import openai
import pandas as pd
from openai.embeddings_utils import get_embedding
import numpy as np
from openai.embeddings_utils import cosine_similarity
from pathlib import Path
import os
from datetime import datetime

app = Flask(__name__)

def get_information(message):
    # Set OpenAI API key
    openai.api_key = os.getenv("OPENAI_API_KEY")
    # open vendors.csv
    THIS_FOLDER = Path(__file__).parent.resolve()
    oferta_file = THIS_FOLDER / "oferta.csv"
    demanda_file = THIS_FOLDER / "demanda.csv"
    # read csv
    df = pd.read_csv(oferta_file,sep='|', encoding='utf-8')
    df['embedding'] = df['embedding'].apply(lambda x: np.array(x[1:-1].split(',')).astype(float))
    # get embedding for message
    message_vector = get_embedding(message, 'text-embedding-ada-002')
    # Calculate cosine similarity
    df['similarity'] = df['embedding'].apply(lambda x: cosine_similarity(x, message_vector))
    # sort by similarity
    df = df.sort_values(by=['similarity'], ascending=False)
    # create a string with the top 20 results that include message, nombre and telefono columns
    prompt = 'Sos un bot argentino, buena onda y amable (con dialecto argentino) que tiene información sobre el pueblo de Quequén. La gente te da información o te pide información y vos respondés acordemente.\nMi mensaje para vos es el siguiente.\n\n"'+message+'"\n\nSi el mensaje suena como un ingreso de información, que la respuesta sea una versión resumida, concreta y útil de la información.\n\nSi el mensaje suena como una consulta (la gente lo puede usar como si fuera una query de Google, ejemplo "panaderia abierta"), responder con información clara, precisa y que ayude usando la siguiente información previamente ingresada:\n\n'+df[['fecha','mensaje']].head(20).to_string(index=False)+'\n\nAdemás, si el mensaje es un ingreso, que tu respuesta empiece con la palabra "INGRESO\n" (con la nueva línea) y si el mensaje es una consulta, que tu respuesta empiece con la palabra "CONSULTA\n" (con la nueva línea). Hablás en tono argentino y amigable. Te divierte que Quequén comience a ser libre finalmente de toda autoridad."'
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
        {"role": "user", "content": prompt}],
    )
    # if the response starts with "INGRESO"
    if response['choices'][0]['message']['content'].startswith('INGRESO'):
        # get the response after it finds '\n'
        print(response['choices'][0]['message']['content'])
        response = response['choices'][0]['message']['content'].split('\n')[1]
        # add the response (which is a csv row of mensaje,nombre,telefono) to the csv in utf-8
        with open(oferta_file, 'a', encoding='utf-8') as f:
            # write the response and the vector of the message in utf-8
            now = datetime.now()
            f.write(str(now)+'|'+message+'|'+str(message_vector)+'\n')
        # return the response
        return "¡Se agregó tu información al sistema! Cualquier consulta hablá conmigo."
    # if the response starts with "CONSULTA"
    elif response['choices'][0]['message']['content'].startswith('CONSULTA'):
        # get the response after it finds '\n'
        print(response['choices'][0]['message']['content'])
        response = response['choices'][0]['message']['content'].split('\n')[1]
        with open(demanda_file, 'a', encoding='utf-8') as f:
            # write the response and the vector of the message in utf-8
            now = datetime.now()
            f.write(str(now)+'|'+message+'|'+str(message_vector)+'\n')
        # return the response
        return response
    

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        message = request.form.get('message')
        if message:  # Check if search_term is not None
            response = get_information(message)
            return jsonify(response)
        else:
            return jsonify({"error": "No entendí"})

    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True)