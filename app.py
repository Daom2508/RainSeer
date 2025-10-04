from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import time

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('map.html')

@app.route('/map')
def map_page():
    return render_template('map.html')

@app.route('/get_last_year_temperature', methods=['POST'])
def get_last_year_temperature():
    data = request.get_json()
    lat = data['lat']
    lon = data['lon']
    fecha = data['fecha']

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; RainSeer/1.0)'
        }

        years = [datetime.now().year - i for i in range(1, 6)]
        mes, dia = fecha.split('-')
        temps = []

        for year in years:
            fecha_completa = f"{year}{mes}{dia}"
            url = (
                f"https://power.larc.nasa.gov/api/temporal/daily/point"
                f"?parameters=T2M"
                f"&community=AG"
                f"&longitude={lon}&latitude={lat}"
                f"&start={fecha_completa}&end={fecha_completa}"
                f"&format=JSON"
            )

            response = requests.get(url, headers=headers)
            json_data = response.json()

            try:
                temp = json_data['properties']['parameter']['T2M'][fecha_completa]
                temps.append(temp)
            except KeyError:
                print(f"No data for {fecha_completa}")

            time.sleep(1)

        if temps:
            promedio_temp = round(sum(temps) / len(temps), 2)
            return jsonify({
                'fecha': fecha,
                'years': years,
                'temperaturas': temps,
                'promedio_temperatura': promedio_temp
            })
        else:
            return jsonify({'error': 'No se pudo obtener datos de temperatura para los años seleccionados.'})

    except Exception as e:
        return jsonify({'error': 'Error al obtener datos de temperatura', 'details': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
