from flask import Flask, request, jsonify
from database import init_db, get_db_connection
import requests
from bs4 import BeautifulSoup

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
        # Extrae el encabezado y la descripción de la página, utilizando las etiquetas h1, h2 y p como identificadores
        headlines = [h.get_text(strip=True) for h in soup.find_all('h1')]
        subheaders = [h.get_text(strip=True) for h in soup.find_all('h2')]
        descriptions = [p.get_text(strip=True) for p in soup.find_all('p')]
        # Nota, se debe tomar en cuenta para el futuro que no todas las páginas web tienen un encabezado h1 o una descripción con etiqueta p.
        # En esos casos, revisar la posibilidad de buscar por etiquetas mas generica como title o meta.

        # En la base de datos, no se permite listas, por lo que se convierten a cadenas de texto
        max_length = max(len(headlines), len(subheaders), len(descriptions))
        headlines = headlines + [''] * (max_length - len(headlines))
        subheaders = subheaders + [''] * (max_length - len(subheaders))
        descriptions = descriptions + [''] * (max_length - len(descriptions))
    
        # Guardar resultados en la base de datos
        conn = get_db_connection()
        c = conn.cursor()
        scraped_data = []
        
        # Se insertan los resultados en la tabla scrape_results, ciclando sobre las listas de encabezados, subencabezados y descripciones
        for headline, subheader, description in zip(headlines, subheaders, descriptions):
            c.execute('''
                INSERT INTO scrape_results (url, headline, subheader, description)
                VALUES (?, ?, ?, ?)
            ''', (url, headline, subheader, description))
            # Guardado de datos para la respuesta
            scraped_data.append({
                'url': url,
                'headline': headline,
                'subheader': subheader,
                'description': description
            })

        conn.commit()
        conn.close()
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({"status": "success", "data": scraped_data}), 200

if __name__ == '__main__':
    app.run(debug=True)