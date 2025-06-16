from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/")
def home():
    return "Chatbot ativo!"

@app.route("/sms", methods=["POST"])
def sms_reply():
    """Responde a mensagens SMS com uma mensagem simples"""
    msg = request.form.get('Body')

    # Criar resposta
    resp = MessagingResponse()
    resp.message(f"Você disse: {msg}")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
