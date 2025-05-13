from flask import Flask, request, render_template_string
import requests
from dotenv import load_dotenv
import os

# Initialize Flask app and load .env variables
app = Flask(__name__)
load_dotenv()

# API Keys
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# HTML Template
HTML_TEMPLATE = """
<!doctype html>
<title>Weather & Food App</title>
<h2>Enter a city to get the current weather and food/travel recommendations</h2>
<form method="post">
    <input name="city" placeholder="City name" required>
    <button type="submit">Submit</button>
</form>

{% if weather %}
    <h3>Weather in {{ city }}:</h3>
    <p>{{ weather }}</p>
{% endif %}

{% if food %}
    <h3>Recommended Regional Food and places to visit in {{ city }}:</h3>
    <p>{{ food }}</p>
{% endif %}

{% if error %}
    <p style="color:red;">{{ error }}</p>
{% endif %}
"""

# Weather function using OpenWeatherMap
def get_weather_for_city(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            return None, data.get("message", "An error occurred.")

        description = data["weather"][0]["description"].capitalize()
        temperature = data["main"]["temp"]
        return f"{description}, {temperature}°C", None
    except Exception as e:
        return None, str(e)

# Food recommendation function using Together.ai
def get_food_recommendation(city):
    try:
        if not TOGETHER_API_KEY:
            return "Together.ai API key not loaded."

        url = "https://api.together.xyz/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
        }

        prompt = f"What is a popular traditional food and places to visit from {city}? show only the names in bullet points in seperate sections, seperating resuts for food and places"

        payload = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        return result["choices"][0]["message"]["content"].strip()
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as e:
        return f"Error getting food recommendation: {e}"
    
# Main route
@app.route("/", methods=["GET", "POST"])
def weather_and_food():
    weather = None
    food = None
    error = None
    city = None

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        if city:
            weather, weather_error = get_weather_for_city(city)
            food = get_food_recommendation(city)
            error = weather_error

    return render_template_string(HTML_TEMPLATE, weather=weather, food=food, error=error, city=city)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
