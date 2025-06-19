from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from supabase import create_client
import os

app = Flask(__name__)
app.secret_key = 'chave-secreta-super-segura'  # altere para algo seguro

# Configuração Supabase (use sua url e chave)
url = "https://mbyuhxjbwmvbhpieywjm.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ieXVoeGpid212YmhwaWV5d2ptIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAxODM0ODAsImV4cCI6MjA2NTc1OTQ4MH0.TF2gFOBExvn9FXb_n8gII-6FGf_NUc1VYvqk6ElCXAM"
supabase = create_client(url, key)

@app.route("/")
def home():
    return "Bot está ativo no Render!"

@app.route("/sms", methods=["POST"])
def sms_reply():
    msg = request.form.get("Body", "").strip()
    resp = MessagingResponse()

    # Inicializa estado da sessão
    if "state" not in session:
        session["state"] = "start"

    # Estado start: pergunta ganho
    if session["state"] == "start":
        resp.message("Olá! Digite 1 para inserir o ganho de hoje, 2 para ver saldo, 3 para sair.")
        session["state"] = "menu"

    # Menu para escolha
    elif session["state"] == "menu":
        if msg == "1":
            resp.message("Digite o valor do seu ganho bruto:")
            session["state"] = "waiting_gain"
        elif msg == "2":
            # Aqui podemos buscar dados no supabase e mostrar saldo (exemplo simples)
            # Para simplificar, mostramos mensagem fixa
            resp.message("Para ver o saldo, use o bot local.")
            session["state"] = "start"
        elif msg == "3":
            resp.message("Bot encerrado. Até logo!")
            session.clear()
        else:
            resp.message("Opção inválida. Digite 1, 2 ou 3.")

    elif session["state"] == "waiting_gain":
        try:
            ganho = float(msg.replace(",", "."))
            session["ganho"] = ganho
            resp.message("Agora digite o valor gasto com combustível:")
            session["state"] = "waiting_fuel"
        except ValueError:
            resp.message("Por favor, digite um número válido para o ganho.")

    elif session["state"] == "waiting_fuel":
        try:
            combustivel = float(msg.replace(",", "."))
            ganho = session.get("ganho", 0)
            liquido = ganho - combustivel

            # Salva no Supabase
            supabase.table("ganhos").insert({
                "bruto": ganho,
                "liquido": liquido
            }).execute()

            resp.message(f"Seu ganho líquido hoje é: R$ {liquido:.2f}")
            session.clear()
        except ValueError:
            resp.message("Por favor, digite um número válido para o combustível.")

    else:
        resp.message("Erro inesperado. Vamos recomeçar.")
        session.clear()

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
