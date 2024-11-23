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
import base64
import openai
from openai import OpenAI

def main():
    # Set page configuration for full screen layout
    st.set_page_config(layout="wide")

    # Set the layout to have 2 columns that scale dynamically to the full width
    col1, col2 = st.columns([1, 2], gap="medium")  # Set column widths: 1/3 for col1, 2/3 for col2

    # Initialize chat history in session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []


     # Column 1: User Input Section
    with col1:
        st.header("Wie kann ich Dir helfen?")  # Title for the left column
        user_input = st.text_area("Deine Frage hier eingeben:", key="user_input", height=150, help="Bitte hier die Frage eingeben")  # Text area for user input, highlighted
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)  # Add margin between text area and file uploader
        col_submit, col_new_chat = st.columns([2, 1], gap="medium")
        with col_submit:
            submit_button = st.button("Absenden", key="submit")  # Submit button, left aligned
        with col_new_chat:
            new_chat_button = st.button("Neuer Chat", key="new_chat")  # New chat button, right aligned

        st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)  # Add margin between buttons and file uploader

        uploaded_file = st.file_uploader("Falls gewünscht, lade ein Bild hoch ...", accept_multiple_files=False, type=["png", "jpg", "jpeg", "webp", "gif"], key="uploaded_file")
        if uploaded_file:
            st.image(uploaded_file, caption="Hochgeladenes Bild", use_container_width=True)  # Display uploaded image with a fixed height of 100 pixels

        if new_chat_button:
            # Clear the session state
            st.session_state.chat_history = []
            st.rerun()  # Rerun to refresh UI components


    # Handle the submission when the button is clicked
    if submit_button:
        # Check if neither text nor file is provided
        if not user_input and not uploaded_file:
            st.warning("Please provide either a text prompt or upload a file before submitting.")  # Warn if no input is provided
        # Check if the uploaded file exceeds the maximum size
        elif uploaded_file and uploaded_file.size > 10 * 1024 * 1024:
            st.error("The uploaded file exceeds the maximum size of 10 MB. Please upload a smaller file.")  # Display error for large files
        # Check if the uploaded file is of an unsupported type
        else:
            # If inputs are valid, process them
         with col2:
            st.write("Deine Eingabe wurde empfangen. Verarbeitung läuft...")
            try:
                response, updated_chat_history = call_gpt4_api(user_input, uploaded_file, st.session_state.chat_history)  # Call process_input to handle the provided inputs
                st.session_state.chat_history = updated_chat_history  # Update the chat history in session state
            except Exception as e:
                with col2:
                    st.error(f"Ein unerwarteter Fehler ist während der 'process_input' Verarbeitung aufgetreten: {str(e)}")  # Display an error if something goes wrong

    # Column 2: Display Chat History
    with col2:
        st.header("Chat Verlauf")
        chat_history_text = ""
        for entry in reversed(st.session_state.chat_history):
            if entry['role'] == 'user':
                chat_history_text += f"<div style='text-align: right; color: green; margin-bottom: 10px;'>{entry['content']}</div><br>\n"
            else:
                chat_history_text += f"<div style='text-align: left; margin-bottom: 10px;'>{entry['content']}</div><br>\n"

        # Display chat history with HTML formatting inside a scrollable container
        st.markdown(f"<div style='height: calc(100vh - 150px); overflow-y: scroll; padding-right: 10px;'>{chat_history_text}</div>", unsafe_allow_html=True)

# Function to encode the image
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def call_gpt4_api(user_input, uploaded_file=None, chat_history=[]):
    # Calling OpenAI's GPT-4 API
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))  # Initialize OpenAI client with API key from environment variables

    system_prompt = """You are an educational assistant for Year 12 A-Level students studying Psychology, Biology, and Geography.
                    Your role is to provide accurate answers and guide students in understanding how to derive those answers themselves.
                    When responding:
                    - Explain Reasoning: Always explain the steps or concepts behind your answer, referencing relevant theories, processes, or data.
                    - Curriculum-Aligned: Use terminology and examples aligned with A-Level standards in these subjects.
                    - Clear and Supportive: Keep explanations clear and supportive, ensuring students feel encouraged and confident.
                    """

    # Prepare the conversation context messages
    messages = [{"role": "system", "content": system_prompt}] + chat_history
    if uploaded_file:
        # Encode the image if provided
        base64_image = encode_image(uploaded_file)
        # Add user input to chat history
        messages.append(
            {"role": "user", "content": [
                {"type": "text", "text": user_input},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        )
    else:
        messages.append({"role": "user", "content": user_input})

    try:
        # Make the API call to GPT-4 with the provided messages
        response = client.chat.completions.create(
          model="gpt-4o",
          messages=messages,
          temperature=0.6,
        )

        # Extract assistant response
        assistant_response = response.choices[0].message.content.strip()

        # Add assistant response to chat history
        chat_history+=[{"role": "user", "content": user_input},{"role": "assistant", "content": assistant_response}]

        return assistant_response, chat_history  # Return both response and updated chat history

    except openai.APIError as e: # Handle API error here, e.g., retry or log
        return f"OpenAI API returned an API Error: {str(e)}", chat_history

if __name__ == "__main__":
    main()  # Run the main function to start the Streamlit app
