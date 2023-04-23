# Red Quequén 🚀🌊🇦🇷

¡Hola! Bienvenidos al repositorio de Red Quequén, un chatbot argentino canchero, buena onda y amigable que te ayuda a compartir información sobre el pueblo de Quequén. Si sos principiante en todo esto de Python, Git, la terminal de Windows y demás, no te preocupes, acá te vamos a explicar todo paso a paso. 😉👍

## Preparando el terreno 🏗️

Antes de empezar, necesitás instalar Python en tu compu. Podés descargarlo de la [página oficial de Python](https://www.python.org/downloads/). Elegí la versión que corresponda a tu sistema operativo y seguí las instrucciones de instalación. ¡No te olvides de marcar la opción de agregar Python al PATH durante la instalación! 😊

## ¿Qué es Git y cómo lo uso? 🤔

Git es una herramienta que nos permite llevar un control de cambios en nuestros proyectos y colaborar con otros desarrolladores. Para usarlo, primero tenés que instalarlo desde la [página oficial de Git](https://git-scm.com/downloads).

Una vez instalado, abrí la terminal de Windows (CMD) o la consola Git Bash (si elegiste instalarla) y asegurate de que git esté instalado correctamente ejecutando `git --version`. Te debería mostrar la versión de Git que instalaste.

## Clonando el repositorio 🧪

Para obtener una copia del proyecto en tu compu, vamos a clonar el repositorio. Ejecutá el siguiente comando en la terminal:

```
git clone https://github.com/tu_usuario/red_quequen.git
```

Reemplazá "tu_usuario" con tu nombre de usuario de GitHub. Ahora tendrías una copia del proyecto en tu compu en la carpeta "red_quequen".

## Instalando las dependencias 📦

Para que Red Quequén funcione correctamente, necesitamos instalar algunas bibliotecas de Python. Para hacerlo, navegá a la carpeta del proyecto en la terminal usando el comando `cd`:

```
cd red_quequen
```

Ahora, vamos a instalar las dependencias ejecutando el siguiente comando:

```
pip install -r requirements.txt
```

Esto instalará todas las bibliotecas necesarias para que el proyecto funcione. ¡Ya casi estamos! 🎉

## Configurando las claves API 🔑

Red Quequén utiliza la API de OpenAI para generar respuestas a las preguntas. Para que funcione, necesitás obtener una clave API de OpenAI. Podés obtenerla creando una cuenta en [OpenAI](https://beta.openai.com/signup/) y siguiendo las instrucciones para obtener tu clave.

Una vez que tengas la clave, creá un archivo llamado `ai_key.txt` en la carpeta del proyecto y pegá la clave API dentro del archivo. Guardá y cerrá el archivo.

## ¡A probar el chatbot! 🤖

Con todo listo, ahora sí podemos probar el chatbot. Ejecutá el siguiente comando en la terminal:

```
python app.py
```

Esto iniciará el servidor de Flask y podrás acceder al chatbot desde tu navegador web. Abrí tu navegador y navegá a `http://localhost:5000`. ¡Listo! Ahora podés empezar a chatear con Red Quequén y compartir información sobre el pueblo. 🏘️🌅

## ¿Cómo colaborar? 🤝

Si querés colaborar con el proyecto, podés hacerlo a través de GitHub. Creá una cuenta (si aún no la tenés), hacé un "fork" del repositorio (esto crea una copia del proyecto en tu cuenta de GitHub), realizá los cambios que quieras y luego enviá un "pull request" para que los cambios sean revisados y, eventualmente, incorporados al proyecto original.

---

¡Eso es todo, amigos! Esperamos que disfrutes de Red Quequén y te diviertas compartiendo información sobre el pueblo. Si tenés alguna duda o sugerencia, no dudes en contactarnos. ¡Hasta la próxima! 😄👋
