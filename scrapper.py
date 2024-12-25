from flask import Flask, request, jsonify
from database import init_db, get_db_connection
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

app = Flask(__name__)

init_db()

#TODO 1: Hacer limpieza de parametros, ya que se esta tomando cosas de la barra de navegacion (etiquetas nav, footer, etc) y no solo del contenido principal de la pagina, tambien agregar excepciones cuando el contenido de la etiqueta p solo sea un punto o un espacio.
#DONE

#TODO 2: Los parrafos se acumulen hasta encontrar un nuevo h3,h2 o h1, para mantener la jerarquia y orden del contenido.

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
        # Definirle luego un modelo de resumen, actualmente utiliza el modelo sshleifer/distilbart-cnn-12-6, revision a4f8f3e
        summarizer = pipeline('summarization', model= 'facebook/bart-large-cnn')
        # Traduce el texto ingresado a ingles
        translated_text = translator_to_english(text)[0]['translation_text']
        # Resume el texto traducido a ingles
        summary_in_english = summarizer(translated_text, max_length=200, min_length=30, do_sample=False)[0]['summary_text']
        # Traduce el resumen a español
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
    
# Ruta para obtener parrafos desde URL y luego conseguir el resumen
@app.route('/combined', methods=['POST'])
def combined():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        for element in soup(['nav', 'footer']):
            element.decompose()
        paragraphs = [p.get_text(strip=True) for p in soup.find_all('p') if p.get_text(strip=True) not in ['.', '']]
        if not paragraphs:
            return jsonify({'error': 'No content found on the page'}), 400
        for element in soup(['nav', 'footer']):
            element.decompose()
        text = ' '.join(paragraphs)

        # Inicializar modelo de IA para resumir texto
        translator_to_english = pipeline("translation", model="Helsinki-NLP/opus-mt-es-en")
        translator_to_spanish = pipeline("translation", model="Helsinki-NLP/opus-mt-en-es")
        summarizer = pipeline('summarization', model= 'facebook/bart-large-cnn')

        # Dividir el texto en partes más pequeñas, debido a que el modelo de traducción tiene un límite de longitud de texto
        max_length = 512
        text_chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
        summary_in_english = ""
        for chunk in text_chunks:
                    translated_text = translator_to_english(chunk)[0]['translation_text']
                    summary_chunk = summarizer(translated_text, max_length=50, min_length=5, do_sample=False)[0]['summary_text']
                    summary_in_english += summary_chunk + " "

        summary_in_spanish = translator_to_spanish(summary_in_english.strip())[0]['translation_text']

        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO combined_results (url, description, input_text, output_text)
            VALUES (?, ?, ?, ?)
        ''', (url, text, summary_in_english, summary_in_spanish))
        conn.commit()
        conn.close()

        return jsonify({"status": "success",
                        "original_text": text,
                        "summary": summary_in_spanish}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)