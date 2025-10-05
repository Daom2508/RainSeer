from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import time

app = Flask(__name__)

# Página principal (inicio de sesión)
@app.route('/')
def index():
    return render_template('index.html')

# Login
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    # Validación básica
    if username and password:
        return render_template('user.html', username=username)
    else:
        error = "Usuario o contraseña incorrectos"
        return render_template('index.html', error=error)

# Página de usuario (elige actividad)
@app.route('/user')
def user_page():
    return render_template('user.html', username="Usuario")

# Showcase (opcional)
@app.route('/showcase')
def showcase():
    return render_template('showcase.html')

# Mapa principal
@app.route('/map')
def map_page():
    return render_template('map.html')

@app.route('/get_weather_summary', methods=['POST'])
def get_weather_summary():
    data = request.get_json()
    lat = data['lat']
    lon = data['lon']
    fecha = data['fecha']

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; RainSeer/1.0)'
        }

        years = [datetime.now().year - 1 - i for i in range(1, 6)]
        mes, dia = fecha.split('-')
        temps = []
        rainfalls = []
        clouds = []
        humidities = []

        for year in years:
            fecha_completa = f"{year}{mes}{dia}"

            # --- Temperatura ---
            url_temp = (
                f"https://power.larc.nasa.gov/api/temporal/daily/point"
                f"?parameters=T2M"
                f"&community=AG"
                f"&longitude={lon}&latitude={lat}"
                f"&start={fecha_completa}&end={fecha_completa}"
                f"&format=JSON"
            )
            response_temp = requests.get(url_temp, headers=headers)
            json_temp = response_temp.json()

            try:
                temp = json_temp['properties']['parameter']['T2M'][fecha_completa]
                temps.append(temp)
            except KeyError:
                print(f"No temperature data for {fecha_completa}")

            # --- Precipitación ---
            url_rain = (
                f"https://power.larc.nasa.gov/api/temporal/daily/point"
                f"?parameters=PRECTOTCORR"
                f"&community=AG"
                f"&longitude={lon}&latitude={lat}"
                f"&start={fecha_completa}&end={fecha_completa}"
                f"&format=JSON"
            )
            response_rain = requests.get(url_rain, headers=headers)
            json_rain = response_rain.json()

            try:
                rainfall = json_rain['properties']['parameter']['PRECTOTCORR'][fecha_completa]
                rainfalls.append(rainfall)
            except KeyError:
                print(f"No rainfall data for {fecha_completa}")

            # ---------Cloudy ------>
            url_cloud = (
                f"https://power.larc.nasa.gov/api/temporal/daily/point"
                f"?parameters=CLOUD_AMT"
                f"&community=AG"
                f"&longitude={lon}&latitude={lat}"
                f"&start={fecha_completa}&end={fecha_completa}"
                f"&format=JSON"
            )
            response_cloud = requests.get(url_cloud, headers=headers)
            json_cloudy = response_cloud.json()

            try:
                cloud= json_cloudy['properties']['parameter']['CLOUD_AMT'][fecha_completa]
                clouds.append(cloud)
            except KeyError:
                print(f"No cloud data for {fecha_completa}")

            url_humidity = (
                f"https://power.larc.nasa.gov/api/temporal/daily/point"
                f"?parameters=RH2M"
                f"&community=AG"
                f"&longitude={lon}&latitude={lat}"
                f"&start={fecha_completa}&end={fecha_completa}"
                f"&format=JSON"
            )
            response_humidity = requests.get(url_humidity, headers=headers)
            json_humidity = response_humidity.json()

            try:
                humid = json_humidity['properties']['parameter']['RH2M'][fecha_completa]
                humidities.append(humid)
            except KeyError:
                print(f"No humidity data for {fecha_completa}")

            time.sleep(1)

        if temps:
            promedio_temp = round(sum(temps) / len(temps), 2)
            promedio_rainfalls = round(sum(rainfalls) / len(rainfalls), 2)
            promedio_cloudy = round(sum(clouds) / len(clouds), 2)
            promedio_humidity = round(sum(humidities) / len(humidities), 2)
            return jsonify({
                'fecha': fecha,
                'promedio_temperatura': promedio_temp,
                'promedio_precipitaciones': promedio_rainfalls,
                'promedio_cloudy': promedio_cloudy,
                'promedio_humidity': promedio_humidity
            })
        else:
            return jsonify({'error': 'No se pudo obtener datos de temperatura para los años seleccionados.'})

    except Exception as e:
        return jsonify({'error': 'Error al obtener datos de temperatura', 'details': str(e)})


if __name__ == '_main_':
    app.run(debug=True)