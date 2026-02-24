from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(__name__)
CORS(app)

# Lấy API KEY từ biến môi trường
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

# ===== GIAO DIỆN =====
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Chat Tư Vấn</title>
<style>
body { margin:0; font-family:Arial; }

#chatBtn {
    position:fixed;
    bottom:20px;
    right:20px;
    width:60px;
    height:60px;
    background:#4CAF50;
    border-radius:50%;
    color:white;
    font-size:28px;
    text-align:center;
    line-height:60px;
    cursor:pointer;
}

#chatBox {
    position:fixed;
    bottom:90px;
    right:20px;
    width:320px;
    height:420px;
    background:white;
    border-radius:15px;
    box-shadow:0 0 15px rgba(0,0,0,0.2);
    display:none;
    flex-direction:column;
}

#header {
    background:#4CAF50;
    color:white;
    padding:12px;
    border-radius:15px 15px 0 0;
}

#messages {
    flex:1;
    padding:10px;
    overflow-y:auto;
    font-size:14px;
}

.msg { margin:8px 0; }
.user { text-align:right; color:#2196F3; }
.bot { text-align:left; color:#333; }

#inputArea {
    display:flex;
    border-top:1px solid #ddd;
}

#inputArea input {
    flex:1;
    border:none;
    padding:10px;
}

#inputArea button {
    border:none;
    background:#4CAF50;
    color:white;
    padding:10px 15px;
}
</style>
</head>
<body>

<div id="chatBtn" onclick="toggleChat()">💬</div>

<div id="chatBox">
    <div id="header">Tư vấn Online</div>
    <div id="messages">
        <div class="msg bot">Xin chào 👋 Tôi có thể giúp gì cho bạn?</div>
    </div>
    <div id="inputArea">
        <input id="msg" placeholder="Nhập câu hỏi...">
        <button onclick="send()">Gửi</button>
    </div>
</div>

<script>
function toggleChat(){
    let box=document.getElementById("chatBox");
    box.style.display = box.style.display==="flex" ? "none" : "flex";
}

async function send(){
    let msg=document.getElementById("msg").value;
    if(!msg) return;

    let messages=document.getElementById("messages");
    messages.innerHTML += "<div class='msg user'>"+msg+"</div>";
    document.getElementById("msg").value="";

    let res=await fetch("/chat",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({message:msg})
    });

    let data=await res.json();
    messages.innerHTML += "<div class='msg bot'>"+data.reply+"</div>";
    messages.scrollTop = messages.scrollHeight;
}
</script>

</body>
</html>
"""

@app.route("/")
def home():
    return HTML

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    response = model.generate_content(
        f"Bạn là trợ lý tư vấn chuyên nghiệp. Trả lời ngắn gọn, dễ hiểu.\n\nKhách hỏi: {user_message}"
    )

    return jsonify({"reply": response.text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
