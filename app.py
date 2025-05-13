from flask import Flask, request, redirect, url_for, render_template_string

app = Flask(__name__)

from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

API_KEY = "YO80ad90f7c743aad83bbd0efb8244400c"  # <-- Replace with your real API key

HTML_TEMPLATE = """
<!doctype html>
<title>Weather App</title>
<h2>Enter a city to get the current weather</h2>
<form method="post">
    <input name="city" placeholder="City name" required>
    <button type="submit">Get Weather</button>
</form>

{% if weather %}
    <h3>Weather in {{ city }}:</h3>
    <p>{{ weather }}</p>
{% elif error %}
    <p style="color:red;">{{ error }}</p>
{% endif %}
"""

def get_weather_for_city(city):
    try:
        url = (
            f"http://api.openweathermap.org/data/2.5/weather?q={city}"
            f"&appid={API_KEY}&units=metric"
        )
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            return None, data.get("message", "An error occurred.")

        description = data["weather"][0]["description"].capitalize()
        temperature = data["main"]["temp"]
        return f"{description}, {temperature}°C", None
    except Exception as e:
        return None, str(e)

@app.route("/", methods=["GET", "POST"])
def weather():
    weather = None
    error = None
    city = None

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        if city:
            weather, error = get_weather_for_city(city)

    return render_template_string(HTML_TEMPLATE, weather=weather, error=error, city=city)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)

