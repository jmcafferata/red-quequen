# Asistente de información basado en GPT-4 🤖

¡Hola! 👋 Este es un programa desarrollado en Python 🐍 que utiliza el modelo GPT-4 de OpenAI para brindar información relevante a partir de archivos de texto o PDF. El programa también cuenta con una interfaz web amigable para facilitar su uso. 🌐

## ¿Qué hace el programa? 🧐

El programa realiza las siguientes acciones:

- Toma archivos de texto (.txt) o PDF (.pdf) de una carpeta llamada input y extrae su contenido
- Divide el contenido en fragmentos más pequeños para facilitar su procesamiento por el modelo GPT-4
- Vectoriza cada fragmento utilizando el modelo text-embedding-ada-002 de OpenAI, lo que nos permite comparar y encontrar información relevante más adelante
- Almacena los fragmentos vectorizados en un archivo JSON llamado output.json en la carpeta vectorized
- El usuario puede interactuar con el programa a través de una interfaz web, donde pueden ingresar consultas o preguntas
- El programa busca en los fragmentos vectorizados almacenados y devuelve la información más relevante según la consulta del usuario

## Instalación y configuración 🛠️

Para instalar y configurar el programa, sigue los siguientes pasos:

1. Asegúrate de tener instalado Python 3.x en tu computadora
2. Instala las bibliotecas requeridas ejecutando el siguiente comando en tu terminal o símbolo del sistema:

   ```
   pip install -r requirements.txt
   ```
   
3. Coloca tus archivos de texto o PDF en la carpeta input
4. Ejecuta el siguiente comando para vectorizar el contenido de los archivos y almacenarlos en el archivo output.json:

   ```
   python vectorize.py
   ```
   
5. Inicia la aplicación web ejecutando el siguiente comando:

   ```
   python app.py
   ```
   
6. Abre tu navegador y visita [http://localhost:5000](http://localhost:5000) para comenzar a interactuar con el programa

## Interfaz web 🌟

La aplicación cuenta con dos páginas web:

- La página principal te permitirá realizar consultas y obtener respuestas a tus preguntas
- La página de administrador (accesible en [http://localhost:5000/admin](http://localhost:5000/admin)) ofrece funcionalidades adicionales para usuarios avanzados

## Importante 💡

Este programa está diseñado para brindar información relevante y útil, pero es posible que no siempre sea 100% precisa. Además, el conocimiento del modelo se basa en datos hasta septiembre de 2021, por lo que puede no estar actualizado con la información más reciente.

¡Diviértete explorando y obteniendo respuestas a tus preguntas! 🎉
