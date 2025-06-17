from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import json

app = Flask(__name__)

DATA_FILE = "dados.json"

# Função para carregar dados
def carregar_dados():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# Função para salvar dados
def salvar_dados(dados):
    with open(DATA_FILE, "w") as f:
        json.dump(dados, f)

# Função principal da rota /sms
@app.route("/sms", methods=["POST"])
def sms_reply():
    numero = request.form.get("From")
    msg = request.form.get("Body").strip()
    dados = carregar_dados()

    if numero not in dados:
        dados[numero] = {
            "estado": "menu",
            "ganhos": [],
            "combustiveis": []
        }

    usuario = dados[numero]
    estado = usuario["estado"]
    resposta = MessagingResponse()

    if estado == "menu":
        if msg == "1":
            usuario["estado"] = "aguardando_ganho"
            resposta.message("Qual é o valor do ganho hoje?")
        elif msg == "2":
            total_bruto = sum(usuario["ganhos"])
            total_combustivel = sum(usuario["combustiveis"])
            total_liquido = total_bruto - total_combustivel
            resposta.message(f"Total bruto: R$ {total_bruto:.2f}\nTotal líquido: R$ {total_liquido:.2f}")
        elif msg == "3":
            resposta.message("Saindo... (Envie qualquer mensagem para voltar ao menu)")
        else:
            resposta.message("Escolha uma opção:\n1 - Adicionar ganhos do dia\n2 - Ver total bruto e líquido\n3 - Sair")
    elif estado == "aguardando_ganho":
        try:
            ganho = float(msg)
            usuario["ganho_temp"] = ganho
            usuario["estado"] = "aguardando_combustivel"
            resposta.message("Quanto gastou de combustível?")
        except ValueError:
            resposta.message("Por favor, digite um valor numérico para o ganho.")
    elif estado == "aguardando_combustivel":
        try:
            combustivel = float(msg)
            ganho = usuario.pop("ganho_temp")
            usuario["ganhos"].append(ganho)
            usuario["combustiveis"].append(combustivel)
            liquido = ganho - combustivel
            resposta.message(f"Ganho registrado!\nValor líquido do dia: R$ {liquido:.2f}")
            usuario["estado"] = "menu"
        except ValueError:
            resposta.message("Por favor, digite um valor numérico para o combustível.")
    else:
        usuario["estado"] = "menu"
        resposta.message("Opção inválida. Retornando ao menu.")

    salvar_dados(dados)
    return str(resposta)

@app.route("/")
def home():
    return "Bot está ativo no Render!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
