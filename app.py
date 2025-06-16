from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Dicionário para armazenar o estado de cada usuário
usuarios = {}

@app.route("/whatsapp", methods=['POST'])
def whatsapp_bot():
    numero = request.form.get('From')
    mensagem = request.form.get('Body').strip()
    resp = MessagingResponse()

    if numero not in usuarios:
        usuarios[numero] = {'etapa': 1}
        resp.message("Olá! Qual é o valor do ganho hoje?")
    elif usuarios[numero]['etapa'] == 1:
        try:
            ganho = float(mensagem.replace(",", "."))
            usuarios[numero]['ganho'] = ganho
            usuarios[numero]['etapa'] = 2
            resp.message("Quanto gastou de combustível?")
        except ValueError:
            resp.message("Por favor, envie apenas o valor do ganho (ex: 100.50).")
    elif usuarios[numero]['etapa'] == 2:
        try:
            combustivel = float(mensagem.replace(",", "."))
            ganho = usuarios[numero]['ganho']
            liquido = ganho - combustivel
            resp.message(f"O valor líquido do ganho de hoje é: R$ {liquido:.2f}")
            usuarios.pop(numero)  # Limpa o estado para nova conversa
        except ValueError:
            resp.message("Por favor, envie apenas o valor gasto com combustível (ex: 50.00).")
    else:
        resp.message("Envie qualquer mensagem para começar.")

    return str(resp)

# Torna o app visível para o gunicorn
if __name__ != "__main__":
    application = app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
