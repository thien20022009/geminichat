import os
from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai

# Lấy API key từ Render Environment
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)

# Lưu lịch sử chat tạm thời (RAM)
chat_history = []

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Gemini Chat Bot</title>
    <style>
        body { font-family: Arial; background: #111; color: white; padding: 20px; }
        .chat-box { max-width: 600px; margin: auto; }
        .msg { margin: 10px 0; }
        .user { color: #00ffcc; }
        .bot { color: #ffcc00; }
        input { width: 80%; padding: 10px; }
        button { padding: 10px; }
    </style>
</head>
<body>
<div class="chat-box">
    <h2>Gemini Chat</h2>
    <div id="chat"></div>
    <input id="msg" placeholder="Nhập tin nhắn..." />
    <button onclick="send()">Gửi</button>
</div>

<script>
async function send() {
    let msg = document.getElementById("msg").value;
    if (!msg) return;

    document.getElementById("chat").innerHTML += 
        "<div class='msg user'>Bạn: " + msg + "</div>";

    document.getElementById("msg").value = "";

    let res = await fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: msg})
    });

    let data = await res.json();

    document.getElementById("chat").innerHTML += 
        "<div class='msg bot'>Bot: " + data.reply + "</div>";
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]

    chat_history.append({"role": "user", "parts": [user_message]})

    response = model.generate_content(chat_history)

    bot_reply = response.text

    chat_history.append({"role": "model", "parts": [bot_reply]})

    return jsonify({"reply": bot_reply})

# KHÔNG cần app.run vì dùng gunicorn
