from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import json

app = Flask(__name__)

DATA_FILE = "dados.json"

def carregar_dados():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {"ganhos": [], "combustiveis": []}

def salvar_dados(dados):
    with open(DATA_FILE, "w") as f:
        json.dump(dados, f)

@app.route("/")
def home():
    return "Bot está ativo no Render!"

@app.route("/sms", methods=["POST"])
def sms_reply():
    numero = request.form.get("From")
    msg = request.form.get("Body").strip().lower()

    print(f"Mensagem recebida de {numero}: {msg}")  # 👈 Isso vai mostrar o que o Twilio enviou

    dados = carregar_dados()
    ganhos = dados["ganhos"]
    combustiveis = dados["combustiveis"]
    resp = MessagingResponse()

    if msg == "1":
        resp.message("Qual foi o ganho de hoje? Envie no formato: ganho:100.00")
    elif msg.startswith("ganho:"):
        try:
            valor = float(msg.split(":")[1])
            dados["ganhos"].append(valor)
            salvar_dados(dados)
            resp.message("Ganho registrado! Agora envie o combustível no formato: combustivel:30.00")
        except:
            resp.message("Formato inválido. Use: ganho:100.00")
    elif msg.startswith("combustivel:"):
        try:
            valor = float(msg.split(":")[1])
            dados["combustiveis"].append(valor)
            salvar_dados(dados)
            liquido = dados["ganhos"][-1] - valor
            resp.message(f"Combustível registrado!\nLucro líquido do dia: R$ {liquido:.2f}")
        except:
            resp.message("Formato inválido. Use: combustivel:30.00")
    elif msg == "2":
        total_bruto = sum(ganhos)
        total_combustivel = sum(combustiveis)
        total_liquido = total_bruto - total_combustivel
        resposta = (
            f"Total bruto: R$ {total_bruto:.2f}\n"
            f"Total líquido: R$ {total_liquido:.2f}"
        )
        resp.message(resposta)
    elif msg == "3":
        resp.message("Encerrando o bot. Até mais!")
    else:
        resp.message("Escolha uma opção:\n1 - Adicionar ganhos do dia\n2 - Ver total\n3 - Sair")

    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
