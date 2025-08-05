from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from supabase import create_client
import os

app = Flask(__name__)
app.secret_key = 'chave-secreta-super-segura'

url = "https://mbyuhxjbwmvbhpieywjm.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ieXVoeGpid212YmhwaWV5d2ptIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAxODM0ODAsImV4cCI6MjA2NTc1OTQ4MH0.TF2gFOBExvn9FXb_n8gII-6FGf_NUc1VYvqk6ElCXAM"
supabase = create_client(url, key)

def tentar_converter_para_float(texto):
    try:
        texto_limpo = texto.strip().replace(",", ".")
        return float(texto_limpo)
    except:
        return None

@app.route("/")
def home():
    return "Bot está ativo!"

@app.route("/sms", methods=["POST"])
def responder_sms():
    msg = request.form.get("Body", "").strip()
    if "estado" not in session:
        session["estado"] = "inicio"

    if session["estado"] == "inicio":
        resposta = MessagingResponse()
        resposta.message("Olá! Digite 1 para inser
