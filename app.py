from flask import Flask, request, redirect, url_for, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<title>Adventure Game</title>
<h2>{{ message }}</h2>

{% if options %}
<form method="post">
  {% for option in options %}
    <button name="choice" value="{{ option }}">{{ option }}</button>
  {% endfor %}
</form>
{% endif %}
"""

# Game logic moved to route handling
@app.route("/", methods=["GET", "POST"])
def game():
    stage = request.args.get("stage", "intro")
    name = request.args.get("name", "")

    if request.method == "POST":
        choice = request.form.get("choice").lower()

        # Handle choices based on stage
        if stage == "intro":
            return redirect(url_for("game", stage=choice, name=name))
        elif stage == "cave":
            if choice == "light":
                return redirect(url_for("game", stage="treasure", name=name))
            elif choice == "tunnel":
                return redirect(url_for("game", stage="trap", name=name))
        elif stage == "treasure" or stage == "trap":
            if choice == "yes":
                return redirect(url_for("game", stage="intro", name=name))
            else:
                return "Thanks for playing!"

    # Handle GET views
    if stage == "intro":
        message = f"Welcome! What's your name?"
        return render_template_string("""
            <!doctype html>
            <form action="/" method="get">
                <input name="name" placeholder="Enter name">
                <input type="hidden" name="stage" value="cave">
                <button type="submit">Start</button>
            </form>
        """)
    elif stage == "cave":
        message = f"{name}, you stand at the entrance of a dark cave. Do you want to enter the LIGHT or the TUNNEL?"
        options = ["light", "tunnel"]
    elif stage == "treasure":
        message = f"{name}, you found a room full of treasure. You win! Play again?"
        options = ["yes", "no"]
    elif stage == "trap":
        message = f"{name}, you fell into a trap. Game over! Play again?"
        options = ["yes", "no"]
    else:
        message = "Invalid stage."
        options = []

    return render_template_string(HTML_TEMPLATE, message=message, options=options)

if __name__ == "__main__":
    app.run(debug=True)
