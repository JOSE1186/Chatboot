from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot está ativo no Render!"

@app.route("/sms", methods=["POST"])
def sms_reply():
    msg = request.form.get("Body")
    resp = MessagingResponse()
    resp.message(f"Você disse: {msg}")
    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
