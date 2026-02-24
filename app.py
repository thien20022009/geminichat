from flask import Flask, request, render_template_string
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)

chat_history = []

html = """
<!DOCTYPE html>
<html>
<head>
<title>Gemini Chat</title>
<style>
body {background:#0f172a;color:white;font-family:Arial;text-align:center;}
.chat-box {background:#1e293b;padding:15px;border-radius:10px;height:400px;overflow-y:auto;}
.user {color:#38bdf8;text-align:right;}
.bot {color:#4ade80;text-align:left;}
input {width:70%;padding:10px;border-radius:10px;border:none;}
button {padding:10px;border-radius:10px;border:none;background:#22d3ee;}
</style>
</head>
<body>
<h2>🤖 Gemini 24/7</h2>
<div class="chat-box">
{% for role, message in history %}
<p class="{{ role }}"><b>{{ role }}:</b> {{ message }}</p>
{% endfor %}
</div>
<form method="post">
<input name="message" required>
<button type="submit">Send</button>
</form>
</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def home():
    global chat_history
    if request.method == "POST":
        user_input = request.form["message"]
        chat_history.append(("user", user_input))
        response = model.generate_content(user_input)
        chat_history.append(("bot", response.text))
    return render_template_string(html, history=chat_history)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
