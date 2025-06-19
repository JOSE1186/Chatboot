from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)
app.secret_key = 'chave-secreta-super-segura'

@app.route("/")
def home():
    return "Bot funcionando no Render!"

@app.route("/sms", methods=["POST"])
def sms_reply():
    resp = MessagingResponse()
    msg = request.form.get("Body", "").strip()

    if "state" not in session:
        session["state"] = "menu"
        session["bruto"] = []
        session["liquido1"] = []
        resp.message("Bot funcionando\n\nMenu:\n1 - Inserir ganho de hoje\n2 - Ver saldo\n3 - Sair")
        return str(resp)

    state = session["state"]
    bruto = session.get("bruto", [])
    liquido1 = session.get("liquido1", [])

    if state == "menu":
        if msg == "1":
            session["state"] = "ganho"
            resp.message("Digite o valor do ganho bruto:")
        elif msg == "2":
            total_bruto = sum(bruto)
            total_liquido = sum(liquido1)
            resp.message(f"Saldo bruto: R$ {total_bruto:.2f}\nSaldo líquido: R$ {total_liquido:.2f}")
        elif msg == "3":
            session.clear()
            resp.message("Bot encerrado")
        else:
            resp.message("Opção inválida. Digite 1, 2 ou 3.")
    elif state == "ganho":
        try:
            valor_bruto = float(msg.replace(",", "."))
            session["valor_bruto"] = valor_bruto
            session["state"] = "gasto"
            resp.message("Digite o valor dos gastos:")
        except ValueError:
            resp.message("Valor inválido. Digite um número para o ganho.")
    elif state == "gasto":
        try:
            combustivel = float(msg.replace(",", "."))
            valor_bruto = session.get("valor_bruto", 0)
            liquido = valor_bruto - combustivel
            bruto.append(valor_bruto)
            liquido1.append(liquido)
            session["bruto"] = bruto
            session["liquido1"] = liquido1
            session["state"] = "menu"
            resp.message("Ganho registrado com sucesso!\n\nMenu:\n1 - Inserir ganho de hoje\n2 - Ver saldo\n3 - Sair")
        except ValueError:
            resp.message("Valor inválido. Digite um número para os gastos.")
    else:
        session.clear()
        resp.message("Erro inesperado. Reiniciando...")
    
    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
