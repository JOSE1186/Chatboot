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
        resposta.message("Olá! Digite 1 para inserir o ganho de hoje, 2 para ver saldo, 3 para sair.")
        session["estado"] = "menu"
        return str(resposta)

    elif session["estado"] == "menu":
        resposta = MessagingResponse()
        if msg == "1":
            resposta.message("Digite o valor do seu ganho bruto:")
            session["estado"] = "aguardando_ganho"
        elif msg == "2":
            dados = supabase.table("ganhos").select("bruto", "liquido").execute()
            if not dados.data:
                resposta.message("Nenhum registro encontrado.")
            else:
                total_bruto = sum(item.get("bruto", 0) for item in dados.data)
                total_liquido = sum(item.get("liquido", 0) for item in dados.data)
                resposta.message(f"🔢 Totais:\nBruto total: R$ {total_bruto:.2f}\nLíquido total: R$ {total_liquido:.2f}")
            session["estado"] = "inicio"
        elif msg == "3":
            resposta.message("Bot encerrado. Até logo!")
            session.clear()
        else:
            resposta.message("Opção inválida. Digite 1, 2 ou 3.")
        return str(resposta)

    elif session["estado"] == "aguardando_ganho":
        ganho = tentar_converter_para_float(msg)
        resposta = MessagingResponse()
        if ganho is not None:
            session["ganho"] = ganho
            resposta.message("Agora digite o valor gasto com combustível:")
            session["estado"] = "aguardando_combustivel"
        else:
            resposta.message("Por favor, envie um número válido. Ex: 100 ou 100.50")
        return str(resposta)

    elif session["estado"] == "aguardando_combustivel":
        combustivel = tentar_converter_para_float(msg)
        resposta = MessagingResponse()
        if combustivel is not None:
            ganho = session.get("ganho", 0)
            liquido = ganho - combustivel

            resultado = supabase.table("ganhos").insert({
                "bruto": ganho,
                "liquido": liquido
            }).execute()

            if resultado.error:
                resposta.message("Erro ao salvar no banco. Tente novamente mais tarde.")
            else:
                resposta.message(f"Seu ganho líquido hoje é: R$ {liquido:.2f}")

            session.clear()
        else:
            resposta.message("Por favor, envie um número válido para o combustível.")
        return str(resposta)

    else:
        resposta = MessagingResponse()
        resposta.message("Erro inesperado. Vamos recomeçar.")
        session.clear()
        return str(resposta)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
