# Standard Helpers
import os

# OpenAI
import openai
openai.api_key = os.getenv('OPENAI_API_KEY')

# PDF Document Loader
from pypdf import PdfReader

# Streamlit
import streamlit as st

file_path = ""

def open_pdf(uploaded_file):
    
    # PDF Datei mit PyPDF laden & Text extrahieren
    if uploaded_file:
        reader = PdfReader(uploaded_file)
        number_of_pages = len(reader.pages)
        pages_text = []
        for page_num in range(0, number_of_pages):
            text = reader.pages[page_num].extract_text()
            pages_text.append(text)

        # Gibt zu Kontrolle im Terminalfenster zusätzliche Informationen aus
        print(f"\nDatei: {file_path}")
        print(f"Umfang: {number_of_pages} Seiten")

        # Das Kapitel mit den Literaturangaben (= 'References') weglassen
        KEY_WORD_ANHANG = 'References' # kennzeichnet im englischen Raum den Beginn des Anhangs
        for seitennr, page in enumerate(pages_text):
            if KEY_WORD_ANHANG in page:
                print(f"Keyword auf Seite {seitennr+1} gefunden")
                pages_text = pages_text[:seitennr]

        # 'all_pages' enthält gesamten PDF-Text als Typ String aber keinerlei Metadaten
        all_pages_text = "\n\n".join(pages_text)
        return number_of_pages, all_pages_text
    else:
        return 0, ""


def create_summary(full_text):
    # Prompt erstellen
    human_message_prompt = f"""
    You will be given one scientific article. Your task is to write a world-class summary. Please make sure you read and understand these instructions very carefully. \

    Your summary will always fulfil the following criteria:
    - Relevance:  The summary should include only important information from the source document and no redundancies or excess information. \
    - Coherence:  The summary should be well-structured and well-organized. The summary should not just be a heap of related information, but should build from sentence to a\
    coherent body of information about a topic.
    - Consistency: A factually consistent summary contains only statements that are entailed by the source document
    - Fluency: the summary has no errors in terms of grammar, spelling, punctuation and is easy to read and follow in terms of word choice and sentence structure.

    Follow the steps:
    - Read the source document carefully
    - Identify the main topics and key points
    - Identify the main facts and details

    Write a long & detailed summary of at least 4-5 paragraphs according to the above criteria.
    Always write the summary in German!

    Scientific Article:

    {full_text}

    Structure of Summary (always in German):
    - Zusammenfassung der Ergebnisse:
        - ...
        - ...
        - ...
    - Zusammenfassung der Schlussfolgerungen:
        - ...
        - ...
        - ...

    - Zusammenfassung der Einschränkungen:
        - ...
        - ...
        - ...

    """
    chat_prompt = [{"role": "user", "content": human_message_prompt }]

    # Aufruf von OpenAI GPT-4 Turbo (ohne Langchain)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", # gpt-4-1106-preview
        temperature=0,
        messages=chat_prompt
    )

    # Gibt zu Kontrolle im Terminalfenster zusätzliche Informationen aus
    print(f"Insgesamt {response['usage']['total_tokens']} Tokens verbraucht für die Zusammenfassung")
    return response.choices[0].message['content']


def save_summary(summary_text):
    st.download_button('Summary speichern', summary_text)
    st.success('Done!')


#
# Erstellt das Fenster mit TKinter Package
#
def main():
    st.title("Laras PDF Summary Generator")

    # Datei-Upload
    uploaded_file = st.file_uploader("Wähle eine PDF-Datei aus", type="pdf")
    if uploaded_file is not None:
        st.success('PDF erfolgreich geladen!', icon="✅")
        
        # Zusammenfassung erstellen
        if st.button('Summary erstellen'):
            # Ersetzen Sie die Logik mit Ihrem PDF-Handling-Code
            num_pages, full_text = open_pdf(uploaded_file) # Diese Funktion muss angepasst werden, um mit Streamlit kompatibel zu sein
            with st.spinner(f'Lese das PDF mit {num_pages} Seiten und erstelle eine Zusammenfassung - das dauert ca 30 Sekunden'):
                summary_text = create_summary(full_text)
            st.text_area("Zusammenfassung", summary_text, height=600)

            # Zusammenfassung speichern
            if st.button('Summary speichern'):
                st.download_button('Summary jetzt speichern', summary_text)
                

# Refresh des Fensters erzwingen zur korrekten Anzeige
if __name__ == "__main__":
    main()