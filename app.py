from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import google.generativeai as genai
import sqlite3
import uuid
import os

app = Flask(__name__)
CORS(app)

# ====== GEMINI CONFIG ======
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# ====== DATABASE ======
def init_db():
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room TEXT,
                    sender TEXT,
                    message TEXT
                )""")
    conn.commit()
    conn.close()

init_db()

# ====== FRONTEND ======
@app.route("/")
def index():
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<title>AI Tư Vấn</title>
<style>
body{
    background:#0f0f0f;
    color:white;
    font-family:Arial;
    margin:0;
}
.header{
    background:#1c1c1c;
    padding:15px;
    text-align:center;
    font-size:20px;
    font-weight:bold;
}
.chat-box{
    padding:15px;
    height:75vh;
    overflow-y:auto;
}
.message{
    margin:10px 0;
    padding:12px 16px;
    border-radius:20px;
    max-width:75%;
}
.user{
    background:#2962ff;
    margin-left:auto;
}
.ai{
    background:#2b2b2b;
}
.input-box{
    display:flex;
    padding:10px;
    background:#1c1c1c;
}
input{
    flex:1;
    padding:10px;
    border:none;
    border-radius:20px;
    outline:none;
}
button{
    background:#2962ff;
    border:none;
    color:white;
    padding:10px 15px;
    margin-left:10px;
    border-radius:20px;
    cursor:pointer;
}
</style>
</head>
<body>

<div class="header">🤖 AI Tư Vấn</div>

<div class="chat-box" id="chat"></div>

<div class="input-box">
    <input id="message" placeholder="Nhập tin nhắn...">
    <button onclick="sendMessage()">Gửi</button>
</div>

<script>
let room = localStorage.getItem("room");
if(!room){
    room = crypto.randomUUID();
    localStorage.setItem("room", room);
}

async function loadMessages(){
    const res = await fetch("/messages?room=" + room);
    const data = await res.json();
    const chat = document.getElementById("chat");
    chat.innerHTML = "";
    data.forEach(msg=>{
        chat.innerHTML += `
        <div class="message ${msg.sender}">
            ${msg.message}
        </div>`;
    });
    chat.scrollTop = chat.scrollHeight;
}

async function sendMessage(){
    const input = document.getElementById("message");
    const text = input.value;
    if(!text) return;

    input.value="";
    await fetch("/chat",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({room:room,message:text})
    });

    loadMessages();
}

loadMessages();
</script>

</body>
</html>
""")

# ====== CHAT API ======
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    room = data["room"]
    user_message = data["message"]

    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("INSERT INTO messages (room,sender,message) VALUES (?,?,?)",
              (room,"user",user_message))
    conn.commit()

    # AI trả lời (tối ưu tốc độ)
    response = model.generate_content(
        user_message,
        generation_config={
            "max_output_tokens": 300,
            "temperature": 0.7
        }
    )

    ai_text = response.text

    c.execute("INSERT INTO messages (room,sender,message) VALUES (?,?,?)",
              (room,"ai",ai_text))
    conn.commit()
    conn.close()

    return jsonify({"reply": ai_text})

# ====== LOAD MESSAGES ======
@app.route("/messages")
def messages():
    room = request.args.get("room")
    conn = sqlite3.connect("chat.db")
    c = conn.cursor()
    c.execute("SELECT sender,message FROM messages WHERE room=?",(room,))
    data = [{"sender":row[0],"message":row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify(data)

if __name__ == "__main__":
    app.run()
