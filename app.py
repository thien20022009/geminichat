from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# ===== GEMINI API =====
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# ===== DATABASE =====
def init_db():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            message TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ===== GIAO DIỆN CHÍNH (CHATBOX) =====
@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Chat</title>
<style>
body{
    margin:0;
    background:#0f0f0f;
    font-family:Arial;
    color:white;
}
#chat{
    max-width:500px;
    margin:auto;
    height:100vh;
    display:flex;
    flex-direction:column;
}
#header{
    padding:15px;
    text-align:center;
    background:#1f1f1f;
    font-size:18px;
    font-weight:bold;
}
#messages{
    flex:1;
    padding:15px;
    overflow-y:auto;
}
.msg{
    margin:10px 0;
    padding:10px 15px;
    border-radius:15px;
    max-width:75%;
}
.user{
    background:#2563eb;
    margin-left:auto;
}
.ai{
    background:#333;
}
#input{
    display:flex;
    padding:10px;
    background:#1f1f1f;
}
#input input{
    flex:1;
    padding:10px;
    border:none;
    border-radius:10px;
    background:#2a2a2a;
    color:white;
}
#input button{
    margin-left:10px;
    padding:10px 15px;
    border:none;
    border-radius:10px;
    background:#2563eb;
    color:white;
}
</style>
</head>
<body>

<div id="chat">
    <div id="header">🤖 AI Tư Vấn</div>
    <div id="messages"></div>
    <div id="input">
        <input id="msg" placeholder="Nhập tin nhắn...">
        <button onclick="send()">Gửi</button>
    </div>
</div>

<script>
async function loadMessages(){
    let res = await fetch("/get_messages");
    let data = await res.json();
    let box = document.getElementById("messages");
    box.innerHTML="";
    data.forEach(m=>{
        box.innerHTML += `<div class='msg ${m.sender}'>${m.message}</div>`;
    });
    box.scrollTop = box.scrollHeight;
}

async function send(){
    let msg = document.getElementById("msg").value;
    if(!msg) return;

    await fetch("/chat",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({message:msg})
    });

    document.getElementById("msg").value="";
    loadMessages();
}

loadMessages();
setInterval(loadMessages,2000);
</script>

</body>
</html>
"""

# ===== API CHAT =====
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    conn = sqlite3.connect("chat.db")
    c = conn.cursor()

    # Lưu user
    c.execute("INSERT INTO messages (sender, message) VALUES (?,?)", ("user", user_message))
    conn.commit()

    # AI trả lời
    response = model.generate_content(user_message)
    ai_reply = response.text

    # Lưu AI
    c.execute("INSERT INTO messages (sender, message) VALUES (?,?)", ("ai", ai_reply))
    conn.commit()
    conn.close()

    return jsonify({"reply": ai_reply})

# ===== LẤY TIN NHẮN =====
@app.route("/get_messages")
def get_messages():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("SELECT sender, message FROM messages")
    data = [{"sender":row[0], "message":row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(data)

# ===== ADMIN =====
@app.route("/admin")
def admin():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("SELECT sender, message FROM messages")
    data = c.fetchall()
    conn.close()

    html = "<h2 style='color:white;background:black;padding:10px'>Admin Panel</h2>"
    html += "<div style='background:black;color:white;padding:15px'>"
    for row in data:
        html += f"<p><b>{row[0]}:</b> {row[1]}</p>"
    html += "</div>"
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
