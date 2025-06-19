from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from supabase import create_client, Client
import os

# Conexão com o Supabase
url = "https://mbyuhxjbwmvbhpieywjm.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ieXVoeGpid212YmhwaWV5d2ptIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAxODM0ODAsImV4cCI6MjA2NTc1OTQ4MH0.TF2gFOBExvn9FXb_n8gII-6FGf_NUc1VYvqk6ElCXAM"
supabase: Client = create_client(url, key)

app = Flask(__name__)
app.secret_key = 'chave-secreta-super-segura'  # mantenha seguro

@app.route("/")
def home():
    return "Bot está ativo no Render!"

@app.route("/sms", methods=["POST"])
def sms_reply():
    msg = request.form.get("Body").strip()
    resp = MessagingResponse()

    if "state" not in session:
        session["state"] = "start"

    if session["state"] == "start":
        resp.message("Olá! Qual é o valor do seu ganho hoje?")
        session["state"] = "waiting_gain"

    elif session["state"] == "waiting_gain":
        try:
            ganho = float(msg.replace(",", "."))
            session["ganho"] = ganho
            resp.message("Quanto você gastou de combustível hoje?")
            session["state"] = "waiting_fuel"
        except ValueError:
            resp.message("Por favor, envie um número válido para o ganho.")

    elif session["state"] == "waiting_fuel":
        try:
            combustivel = float(msg.replace(",", "."))
            ganho = session.get("ganho", 0)
            liquido = ganho - combustivel

            # Salva os dados no Supabase
            supabase.table("ganhos").insert({
                "bruto": ganho,
                "liquido": liquido
            }).execute()

            resp.message(f"O valor líquido do ganho de hoje é: R$ {liquido:.2f}")
            session.clear()  # resetar conversa
        except ValueError:
            resp.message("Por favor, envie um número válido para o combustível.")
    else:
        resp.message("Erro inesperado. Vamos começar novamente.")
        session.clear()

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
