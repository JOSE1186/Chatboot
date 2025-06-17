from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)
app.secret_key = 'chave-super-secreta'

@app.route("/")
def home():
    return "Bot de cálculo de ganhos está ativo!"

@app.route("/sms", methods=["POST"])
def sms_reply():
    msg = request.form.get("Body").strip().lower()
    resp = MessagingResponse()

    if "state" not in session:
        session["state"] = "menu"
        session["ganhos"] = []
        session["combustiveis"] = []

    state = session["state"]

    if state == "menu":
        resp.message(
            "Escolha uma opção:\n1 - Adicionar ganhos do dia\n2 - Ver total bruto e líquido\n3 - Sair"
        )
        session["state"] = "aguardando_opcao"

    elif state == "aguardando_opcao":
        if msg == "1":
            session["state"] = "ganho"
            resp.message("Qual é o valor do ganho hoje?")
        elif msg == "2":
            total_bruto = sum(session["ganhos"])
            total_comb = sum(session["combustiveis"])
            total_liq = total_bruto - total_comb
            resp.message(f"Total bruto: R$ {total_bruto:.2f}\nTotal líquido: R$ {total_liq:.2f}")
            session["state"] = "menu"
        elif msg == "3":
            resp.message("Saindo... até a próxima!")
            session.clear()
        else:
            resp.message("Opção inválida. Por favor, envie 1, 2 ou 3.")

    elif state == "ganho":
        try:
            ganho = float(msg.replace(",", "."))
            session["ganho_temp"] = ganho
            session["state"] = "combustivel"
            resp.message("Quanto gastou de combustível?")
        except ValueError:
            resp.message("Valor inválido. Envie um número para o ganho.")

    elif state == "combustivel":
        try:
            combustivel = float(msg.replace(",", "."))
            ganho = session.pop("ganho_temp", 0)
            session["ganhos"].append(ganho)
            session["combustiveis"].append(combustivel)
            liquido = ganho - combustivel
            resp.message(f"Ganhos do dia registrados!\nLíquido: R$ {liquido:.2f}")
            session["state"] = "menu"
        except ValueError:
            resp.message("Valor inválido. Envie um número para o combustível.")

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
