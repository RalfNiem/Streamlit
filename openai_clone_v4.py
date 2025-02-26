# Dieses Dokument beschreibt die Anforderungen für die Entwicklung einer einfachen Webanwendung,
# die es ermöglicht, Text- und Dateieingaben zu machen, welche über die OpenAI GPT-4 API verarbeitet werden.
# Die Anwendung soll es ermöglichen, die Funktionen von ChatGPT zu nutzen, ohne direkte Zugriffsdaten preiszugeben.
# Sie dient primär dazu, Finja den Zugang in West Buckland zu ermöglichen, ohne dass die OpenAI-Zugangsdaten weitergegeben werden müssen.
#
# Start des Programms:
# 1) OPENAI KEY muss als Systemvariable gesetzt sein
# 2) Ein passendes conda environment muss aktiviert ist zB über 'conda activate langchain_full'
# 3) Programm im Terminal starten mit 'streamlit run openai_clone.py'

import streamlit as st
import os
import io
import fitz  # PyMuPDF
import base64
from PIL import Image
import openai
from openai import OpenAI

OPENAI_MODEL = "gpt-4o"
# Keys einlesen
#from dotenv import load_dotenv, find_dotenv
#_ = load_dotenv(find_dotenv())


def handle_input_submit():
    """Callback for when text input changes"""
    if st.session_state.user_input:
        try:
            call_openai_api()
            st.session_state.user_input = ""
        except Exception as e:
            st.error(f"Ein unerwarteter Fehler ist während der 'handle_input_submit()' aufgetreten: {str(e)}")


def handle_file_upload():
    """Callback for when a file is uploaded"""
    if st.session_state.uploaded_file is not None:
        # Determine file type
        file_extension = st.session_state.uploaded_file.name.lower().split('.')[-1]
        image_extensions = ['png', 'jpg', 'jpeg', 'webp', 'gif']

        if file_extension in image_extensions:
            st.session_state.uploaded_file_type = "Image"
            st.session_state.displayed_image = True

        elif file_extension == 'pdf':
            st.session_state.uploaded_file_type = "PDF"
            st.session_state.displayed_image = True
            # Bytes aus Streamlit-Upload lesen
            #pdf_bytes = st.session_state.uploaded_file.read()
            st.session_state.uploaded_file_stream = io.BytesIO(st.session_state.uploaded_file.read())

        else:
            st.error("Unsupported file type. Please upload an image or PDF file.")
            st.session_state.uploaded_file_type = None
            st.session_state.displayed_image = False
            return
    else:
        st.session_state.uploaded_file_type = None
        st.session_state.displayed_image = False



def clear_chat():
    """Callback to clear the chat"""
    st.session_state.chat_history = []
    st.session_state.user_input = ""
    st.session_state.displayed_image = False


def get_all_text_from_pdf(pdf_stream):
    # Datei öffnen und Text extrahieren
    try:
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        # Text aus allen Seiten extrahieren
        extracted_text = ""
        for page in doc:
            extracted_text += page.get_text("text") + "\n"
        print(f"Länge des Dokuments = {len(doc)} Seiten")
        print(f"Anzahl Zeichen = {len(extracted_text)}")
        return extracted_text

    except Exception as e:
        print(f"Fehler in get_all_text_from_pdf: {e}")


# Function to encode the image
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def call_openai_api():
    # Calling OpenAI's GPT-4 API
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))  # Initialize OpenAI client with API key from environment variables

    system_prompt = """You are an educational assistant for Year 12 A-Level students.
                    Your role is to provide accurate answers and guide students in understanding how to derive those answers themselves.
                    When responding:
                    - Explain Reasoning: Always explain the steps or concepts behind your answer, referencing relevant theories, processes, or data.
                    - Curriculum-Aligned: Use terminology and examples aligned with A-Level standards in these subjects.
                    - Clear and Supportive: Keep explanations clear and supportive, ensuring students feel encouraged and confident.
                    - Only use Markdown format, never Latex format
                    """

    # Prepare the conversation context messages
    messages = [{"role": "system", "content": system_prompt}] + st.session_state.chat_history
    if st.session_state.uploaded_file:
        if st.session_state.uploaded_file_type == "Image":
            # Encode the image if provided
            base64_image = encode_image(st.session_state.uploaded_file)
            # Add user input to chat history
            messages.append(
                {"role": "user", "content": [
                    {"type": "text", "text": st.session_state.user_input},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            )
        elif st.session_state.uploaded_file_type == "PDF":
            pdf_text = get_all_text_from_pdf(st.session_state.uploaded_file_stream)
            user_query = f"*** Inhalt des Dokuments ***\n<Dokument-Text>{pdf_text}</Dokument-Text>\n*** User-Query ***\n<User-Query>{st.session_state.user_input}</User-Query>"
            messages.append({"role": "user", "content": user_query})

    else:
        messages.append({"role": "user", "content": st.session_state.user_input})

    try:
        # Make the API call to GPT-4 with the provided messages
        response = client.chat.completions.create(
          model=OPENAI_MODEL,
          messages=messages,
          temperature=0.6,
        )

        # Extract assistant response
        assistant_response = response.choices[0].message.content.strip()

        # Add assistant response to chat history
        st.session_state.chat_history += [{"role": "user", "content": st.session_state.user_input}, {"role": "assistant", "content": assistant_response}]

    except openai.APIError as e: # Handle API error here, e.g., retry or log
        return f"OpenAI API returned an API Error: {str(e)}", chat_history


# Main UI layout
def main():
    # Initialize session state variables if they don't exist
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""
    if 'displayed_image' not in st.session_state:
        st.session_state.displayed_image = False
    if 'uploaded_file_type' not in st.session_state:
        st.session_state.uploaded_file_type = None
    if 'uploaded_file_text' not in st.session_state:
        st.session_state.uploaded_file_text = ""
    if 'uploaded_file_stream' not in st.session_state:
        st.session_state.uploaded_file_stream = ""

    # Set page configuration for full screen layout
    st.set_page_config(layout="wide")

    # Set the layout to have 2 columns that scale dynamically to the full width
    col1, col2 = st.columns([1, 2], gap="medium")  # Set column widths: 1/3 for col1, 2/3 for col2

    with col1:
        st.header("Wie kann ich Dir helfen?")

        # Text input with callback
        st.text_area(
            "Deine Frage hier eingeben:",
            key="user_input",
            height=150,
            help="Bitte hier die Frage eingeben",
            on_change=handle_input_submit
        )

        #st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

        st.button("Neuen Chat starten ...", on_click=clear_chat)

        #st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

        # File uploader with callback
        st.file_uploader(
            "Falls gewünscht, lade eine Datei hoch ...",
            accept_multiple_files=False,
            type=["pdf", "png", "jpg", "jpeg", "gif"],
            key="uploaded_file",
            on_change=handle_file_upload
        )

        # Display uploaded image if present
        if st.session_state.uploaded_file and st.session_state.displayed_image:
            if st.session_state.uploaded_file_type == "Image":
                st.image(
                    st.session_state.uploaded_file,
                    caption="Hochgeladenes Bild",
                    use_container_width=True
                )
            elif st.session_state.uploaded_file_type == "PDF":
                doc = fitz.open(stream=st.session_state.uploaded_file_stream, filetype="pdf")
                # Erste Seite rendern
                page = doc[0]
                pix = page.get_pixmap()  # Erstellt ein Bildobjekt (Pixmap)

                # Pixmap in ein PIL-Bild umwandeln
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                st.image(img, use_container_width=True)

    # Display chat history and responses in second column
    with col2:
        if st.session_state.chat_history:
            st.header("Chat Verlauf")
            chat_history_text = ""
            for entry in reversed(st.session_state.chat_history):
                if entry['role'] == 'user':
                    chat_history_text += f"<div style='text-align: right; color: green; margin-bottom: 10px;'>{entry['content']}</div><br>\n"
                else:
                    chat_history_text += f"<div style='text-align: left; margin-bottom: 10px;'>{entry['content']}</div><br>\n"

            # Display chat history with HTML formatting inside a scrollable container
            st.markdown(f"<div style='height: calc(100vh - 150px); overflow-y: scroll; padding-right: 10px;'>{chat_history_text}</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()  # Run the main function to start the Streamlit app
