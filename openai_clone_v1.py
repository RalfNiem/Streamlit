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
    # Title and Header
    #st.title("ChatGPT Web Application")  # Set the main title of the web application
    st.subheader("Finja's West Buckland compatible ChatGPT-4")  # Provide a brief header explaining the purpose

    # Text Input Section
    # st.subheader("Your Question:")  # Subheader for text input section
    user_input = st.text_area("Type your question here:")  # Text area for the user to input their message

    # File Upload Section
    #st.subheader("Upload an Image (JPG, PNG or WEBP)")  # Subheader for file upload
    uploaded_file = st.file_uploader("Upload an image", accept_multiple_files=False, type=["png", "jpg", "jpeg", "webp", "gif"])  # File uploader for supported file types

    # Submit Button
    submit_button = st.button("Submit")  # Button to submit the input

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
            st.write("Your input has been received. Processing...")
            try:
                response = call_gpt4_api(user_input, uploaded_file)  # Call process_input to handle the provided inputs
                st.write("Response from GPT-4o:")
                st.write(response)  # Display the response from GPT-4
            except Exception as e:
                st.error(f"An unexpected error occurred during 'process_input': {str(e)}")  # Display an error if something goes wrong

    # Footer and Additional Info
    st.markdown("---")  # Add a horizontal line separator
    #st.markdown("This web application is powered by OpenAI's GPT-4 API. It allows interaction via both text input and image upload for processing queries.")  # Footer description


# Function to encode the image
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')


def call_gpt4_api(user_input, uploaded_file=None):
    # Calling OpenAI's GPT-4 API
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))  # Initialize OpenAI client with API key from environment variables

    system_prompt = """You are an educational assistant for Year 12 A-Level students studying Psychology, Biology, and Geography.
                    Your role is to provide accurate answers and guide students in understanding how to derive those answers themselves.
                    When responding:
                    - Explain Reasoning: Always explain the steps or concepts behind your answer, referencing relevant theories, processes, or data.
                    - Curriculum-Aligned: Use terminology and examples aligned with A-Level standards in these subjects.
                    - Clear and Supportive: Keep explanations clear and supportive, ensuring students feel encouraged and confident.
                    """

    try:
        # Prepare the conversation context messages
        if uploaded_file:
            base64_image = encode_image(uploaded_file)
            messages = [
                {"role": "system", "content": system_prompt}, # System message to set the assistant's behavior
                {"role": "user", "content": [
                    {
                        "type": "text",
                        "text": user_input,
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url":  f"data:image/jpeg;base64,{base64_image}"},
                    },
                    ],
                }
                ]
        else:
            messages = [
                {"role": "system", "content": system_prompt}, # System message to set the assistant's behavior
                {"role": "user", "content": user_input}
                ]

        # Make the API call to GPT-4 with the provided messages
        response = client.chat.completions.create(
          model="gpt-4o-mini",
          messages=messages,
          temperature=0.6,
        )
        return response.choices[0].message.content.strip()  # Return the response text from GPT-4
    except openai.APIError as e: #Handle API error here, e.g. retry or log
        return f"OpenAI API returned an API Error: {str(e)}"

if __name__ == "__main__":
    main()  # Run the main function to start the Streamlit app
