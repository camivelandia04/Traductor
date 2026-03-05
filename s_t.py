import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob

from gtts import gTTS
from googletrans import Translator


st.title("TRADUCTOR DE IDIOMAS ROMANCE")
st.subheader("Escucho lo que quieres traducir.")

# Imagen principal
image = Image.open('OIG7.jpg')
st.image(image,width=300)

# Nueva imagen con idiomas
image2 = Image.open('Apps-de-traduccion.jpg')
st.image(image2, caption="Idiomas Romance disponibles", width=400)

with st.sidebar:
    st.subheader("Traductor.")
    st.write("Presiona el botón, cuando escuches la señal "
                 "habla lo que quieres traducir, luego selecciona"   
                 " la configuración de lenguaje que necesites.")

st.write("Toca el Botón y habla lo que quieres traducir")

stt_button = Button(label=" Escuchar 🎤", width=300, height=50)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'es-ES';
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    
    recognition.onend = function() {
        console.log("Reconocimiento detenido");
    }
    
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

# Diccionario de idiomas romance
romance_languages = {
    "Español": "es",
    "Portugués": "pt",
    "Francés": "fr",
    "Italiano": "it",
    "Rumano": "ro",
    "Catalán": "ca",
    "Gallego": "gl"
}

if result:
    if "GET_TEXT" in result:
        st.write(result.get("GET_TEXT"))

    try:
        os.mkdir("temp")
    except:
        pass

    st.title("Texto a Audio")
    translator = Translator()

    text = str(result.get("GET_TEXT"))

    # Selección de idioma de entrada
    in_lang = st.selectbox(
        "Selecciona el lenguaje de Entrada",
        list(romance_languages.keys()),
    )

    input_language = romance_languages[in_lang]

    # Selección de idioma de salida
    out_lang = st.selectbox(
        "Selecciona el lenguaje de salida",
        list(romance_languages.keys()),
    )

    output_language = romance_languages[out_lang]

    english_accent = st.selectbox(
        "Selecciona el acento",
        (
            "Defecto",
            "España",
            "Estados Unidos",
            "Reino Unido",
        ),
    )

    if english_accent == "Defecto":
        tld = "com"
    elif english_accent == "España":
        tld = "es"
    elif english_accent == "Estados Unidos":
        tld = "com"
    elif english_accent == "Reino Unido":
        tld = "co.uk"


    def text_to_speech(input_language, output_language, text, tld):

        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text

        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)

        try:
            my_file_name = text[0:20]
        except:
            my_file_name = "audio"

        tts.save(f"temp/{my_file_name}.mp3")

        return my_file_name, trans_text


    display_output_text = st.checkbox("Mostrar el texto")

    if st.button("Convertir"):

        result, output_text = text_to_speech(input_language, output_language, text, tld)

        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()

        st.markdown("## Tu audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.markdown("## Texto traducido:")
            st.write(output_text)


    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400

            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)

    remove_files(7)
