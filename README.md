# PDF Summary Generator

## Zusammenfassung
Das Programm nutzt GPT-4 Turbo um für ein PDF-Dokument eine Zusammenfassung zu erstellen  
Als zusätzliches Gimmick, versucht das Prgramm den Titel & Autor des PDFs zu ermitteln  
Als Framework wird lediglich Streamlit für die GUI verwendet, auf Langchain oder LLamaIndex wurde verzichtet
 
## Lokaler Start des Programms:
1) OPENAI KEY muss als Systemvariable gesetzt sein
2) Ein passendes conda environment muss aktiviert ist zB über 'conda activate langchain'
3) Programm im Terminal starten mit 'streamlit run PDF_Summary_Streamlit.py'

Versuche, mit PyInstaller oder py2app eine für OS X und Windows ausführbare Programmversion zu erstellen,
die einen einfachen Programmstart per "Doppelklick" ermöglich, waren nur bedingt erfolgreich

## Aufruf über Internet (= Streamlit Community Cloud)
Die Streamlit Community Cloud ist eine Plattform, die Entwicklern ermöglicht, ihre Streamlit-Apps kostenlos zu hosten und zu teilen. Sie bietet eine einfache und schnelle Möglichkeit, Projekte interaktiv im Web zu präsentieren. Nutzer können ohne komplexe Infrastruktur ihre Apps direkt aus ihrem GitHub-Repository bereitstellen und mit der Community oder einem breiteren Publikum teilen.  

Der Aufruf der App kann prinzipiell von jedem Rechner unter folgender Adresse erfolgen:  
**https://laras-pdf-summary-generator.streamlit.app/**  

Kleiner Disclaimer dazu:
- Dabei muss der entsprechende App-Container erst geladen werden, so dass der Start ca 30 Sekunden dauert, bis der Startbildschirm erscheint
- Um auch tatsächlich von jedem Rechner erreichbar zu sein, muss die App als 'öffentlich' konfiguriert sein. Die Streamlit-App kann [hier](https://share.streamlit.io/) verwaltet werden.
- Da die Streamlit-App direkt mit Github verbunden ist, sind Sourcecode Änderungen sofort im Programm sichtbar.

## Streamlit
Weiterführende Programm-Beispiele zu Streamlit sind auf [Github](https://github.com/streamlit/streamlit) vorhanden

