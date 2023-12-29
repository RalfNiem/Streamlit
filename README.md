# PDF Summary Generator

Das Programm nutzt GPT-4 Turbo um für ein PDF-Dokument eine Zusammenfassung zu erstellen  
Als zusätzliches Gimmick, versucht das Prgramm den Titel & Autor des PDFs zu ermitteln  
Als Framework wird lediglich Streamlit für die GUI verwendet, auf Langchain oder LLamaIndex wurde verzichtet
 
Start des Programms:
1) OPENAI KEY muss als Systemvariable gesetzt sein
2) Ein passendes conda environment muss aktiviert ist zB über 'conda activate langchain'
3) Programm im Terminal starten mit 'streamlit run PDF_Summary_Streamlit.py'
 
Versuche, mit PyInstaller oder py2app eine für OS X und Windows ausführbare Programmversion zu erstellen,
die einen einfachen Programmstart per "Doppelklick" ermöglich, waren nur bedingt erfolgreich
