from flask import Flask, request, render_template_string
import requests
from dotenv import load_dotenv
import os
import markdown

# Initialize Flask app and load .env variables
app = Flask(__name__)
load_dotenv()

# API Keys
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

# HTML Template
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Weather & Food App</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f7fa;
            color: #1f1f1f;
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
            max-width: 600px;
            width: 100%;
            padding: 30px;
            box-sizing: border-box;
        }
        h2, h3 {
            color: #2c3e50;
            margin-bottom: 16px;
        }
        form {
            margin-bottom: 24px;
        }
        input[type="text"], input[name="city"] {
            width: 100%;
            padding: 12px 14px;
            margin-top: 8px;
            margin-bottom: 16px;
            border: 1px solid #dce1e7;
            border-radius: 12px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
        }
        input:focus {
            border-color: #007bff;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #0056b3;
        }
        .card {
            background-color: #f9fafb;
            border-radius: 12px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
        }
        .error {
            color: #d9534f;
            font-weight: 500;
            margin-top: 12px;
        }
        ul {
            padding-left: 20px;
        }
        ul li {
            margin-bottom: 6px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>🌦️ Discover Weather & Regional Insights</h2>
        <form method="post">
            <input name="city" type="text" placeholder="Enter a city" required>
            <button type="submit">Submit</button>
        </form>

        {% if weather %}
        <div class="card">
            <h3>Weather in {{ city }}:</h3>
            <p>{{ weather }}</p>
        </div>
        {% endif %}

        {% if food %}
        <div class="card">
            <h3>Food recommendations for {{ city }}:</h3>
            <div>{{ food | safe }}</div>
        </div>
        {% endif %}

        {% if error %}
        <p class="error">{{ error }}</p>
        {% endif %}
    </div>
</body>
</html>
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

        prompt = (
            f"List 3 traditional foods and 3 popular places from {city} using only the names and no description. "
            f"Respond in Markdown format like this:\n"
            f"- **Food Name**"
            f"- **Place Name**"
        )

        payload = {
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 300
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        markdown_content = result["choices"][0]["message"]["content"].strip()
        html_content = markdown.markdown(markdown_content)
        return html_content
    except Exception as e:
        return f"<p class='error'>Error getting food recommendation: {e}</p>"

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
