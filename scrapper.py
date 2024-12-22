from flask import Flask, request, jsonify
from database import init_db, get_db_connection
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

app = Flask(__name__)

init_db()

#TODO 1: Hacer limpieza de parametros, ya que se esta tomando cosas de la barra de navegacion (etiquetas nav, footer, etc) y no solo del contenido principal de la pagina, tambien agregar excepciones cuando el contenido de la etiqueta p solo sea un punto o un espacio.

# Ruta para realizar scraping de una URL y guardar los resultados en la base de datos
@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        # Realizar scraping
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Eliminar elementos no deseados (navegación, pie de página, etc.)
        for element in soup(['nav', 'footer']):
            element.decompose()
        # Variables para mantener el encabezado actual, ya que se pueden encontrar varios niveles de encabezados y de esta manera se puede mantener la jerarquía y orden del contenido
        current_h1 = ""
        current_h2 = ""
        current_h3 = ""

        # Lista para almacenar los resultados estructurados
        structured_data = []

        # Recorrer todos los elementos relevantes en orden, para mantener la jerarquía y se entienda mejor el contenido
        for element in soup.find_all(['h1', 'h2', 'h3', 'p']):
            text = element.get_text(strip=True)
            # Ignorar elementos no deseados (vacíos, puntos, etc.)
            if text in ['.', '']:
                continue

            if element.name == 'h1':
                current_h1 = text
                current_h2 = ""  # Reiniciar h2 y h3 al encontrar un nuevo h1
                current_h3 = ""
            elif element.name == 'h2':
                current_h2 = text
                current_h3 = ""  # Reiniciar h3 al encontrar un nuevo h2
            elif element.name == 'h3':
                current_h3 = text
            elif element.name == 'p':
                # Asociar el párrafo al encabezado actual
                structured_data.append({
                    'url': url,
                    'headline': current_h1,
                    'subheader': current_h2,
                    'subsubheader': current_h3,
                    'description': text
                })

        # Guardar resultados en la base de datos
        conn = get_db_connection()
        c = conn.cursor()
        scraped_data = []

        for row in structured_data:
            c.execute('''
                INSERT INTO scrape_results (url, headline, subheader, subsubheaders, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (row['url'], row['headline'], row['subheader'], row['subsubheader'], row['description']))

            # Agregar a la lista de datos a devolver
            scraped_data.append(row)

        conn.commit()
        conn.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({"status": "success", "data": scraped_data}), 200

# Ruta de modelo de IA para procesar el texto y resumirlo
@app.route('/process', methods=['POST'])
def process():
    text = request.json.get('text')
    if not text:
        return jsonify({'error': 'Text is required'}), 400

    try:
        # Inicializar modelo de IA para resumir texto
        translator_to_english = pipeline("translation", model="Helsinki-NLP/opus-mt-es-en")
        translator_to_spanish = pipeline("translation", model="Helsinki-NLP/opus-mt-en-es")
        summarizer = pipeline('summarization')

         # Translate text to English
        translated_text = translator_to_english(text)[0]['translation_text']

        # Summarize the translated text
        summary_in_english = summarizer(translated_text, max_length=100, min_length=5, do_sample=False)[0]['summary_text']

        # Translate the summary back to Spanish
        summary_in_spanish = translator_to_spanish(summary_in_english)[0]['translation_text']

        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO processed_results (input_text, output_text)
            VALUES (?, ?)
        ''', (text, summary_in_spanish))
        conn.commit()
        conn.close()

        return jsonify({"status": "success",
                        "summary": summary_in_spanish}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)