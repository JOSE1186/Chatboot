from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json
import os

app = Flask(__name__)

DATA_FILE = "dados.json"

# Inicializa o arquivo se não existir
def init_storage():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)

# Carrega os dados do arquivo
def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Salva os dados no arquivo
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

@app.route("/")
def home():
    return "Bot ativo!"

@app.route("/sms", methods=["POST"])
def sms_reply():
    msg = request.form.get("Body").strip()
    number = request.form.get("From")

    data = load_data()
    user = data.get(number, {"state": "menu", "ganhos": [], "combustiveis": []})

    resp = MessagingResponse()
    response_msg = ""

    if user["state"] == "menu":
        if msg == "1":
            user["state"] = "esperando_ganho"
            response_msg = "Qual é o valor do ganho de hoje?"
        elif msg == "2":
            total_bruto = sum(user["ganhos"])
            total_combustivel = sum(user["combustiveis"])
            total_liquido = total_bruto - total_combustivel
            response_msg = f"\nTotal bruto: R$ {total_bruto:.2f}\nTotal líquido: R$ {total_liquido:.2f}"
        elif msg == "3":
            response_msg = "Saindo... Para iniciar novamente, envie qualquer mensagem."
            user = {"state": "menu", "ganhos": [], "combustiveis": []}
        else:
            response_msg = ("Escolha uma opção:\n1 - Adicionar ganhos do dia\n"
                            "2 - Ver total bruto e líquido\n3 - Sair")

    elif user["state"] == "esperando_ganho":
        try:
            user["ganho_temp"] = float(msg)
            user["state"] = "esperando_combustivel"
            response_msg = "Quanto gastou de combustível?"
        except ValueError:
            response_msg = "Por favor, envie um número válido para o ganho."

    elif user["state"] == "esperando_combustivel":
        try:
            combustivel = float(msg)
            ganho = user.pop("ganho_temp")
            user["ganhos"].append(ganho)
            user["combustiveis"].append(combustivel)
            liquido = ganho - combustivel
            user["state"] = "menu"
            response_msg = f"O valor líquido do ganho de hoje é: R$ {liquido:.2f}"
        except ValueError:
            response_msg = "Por favor, envie um número válido para o combustível."

    data[number] = user
    save_data(data)
    resp.message(response_msg)
    return str(resp)

if __name__ == "__main__":
    init_storage()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
