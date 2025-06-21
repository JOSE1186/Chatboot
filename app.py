from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from supabase import create_client
import os

app = Flask(__name__)
app.secret_key = 'chave-secreta-super-segura'

# 🔐 Configuração do Supabase
url = "https://mbyuhxjbwmvbhpieywjm.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ieXVoeGpid212YmhwaWV5d2ptIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAxODM0ODAsImV4cCI6MjA2NTc1OTQ4MH0.TF2gFOBExvn9FXb_n8gII-6FGf_NUc1VYvqk6ElCXAM"
supabase = create_client(url, key)

# 🔁 Tenta converter um texto em número decimal
def converter_para_float(texto):
    try:
        texto_limpo = texto.strip().replace(",", ".")
        print(f"Texto recebido: '{texto}' | Texto limpo: '{texto_limpo}'")
        return float(texto_limpo)
    except ValueError:
        return None



# 📩 Rota que recebe mensagens do usuário
@app.route("/sms", methods=["POST"])
def responder_mensagem():
    mensagem = request.form.get("Body", "").strip()
    resposta = MessagingResponse()

    # Iniciar sessão se não existir
    if "estado" not in session:
        session["estado"] = "inicio"

    # Mostrar menu principal
    if session["estado"] == "inicio":
        resposta.message("Olá! Digite 1 para inserir o ganho de hoje, 2 para ver saldo, 3 para sair.")
        session["estado"] = "menu"

    elif session["estado"] == "menu":
        if mensagem == "1":
            resposta.message("Digite o valor do seu ganho bruto:")
            session["estado"] = "aguardando_ganho"

        elif mensagem == "2":
            try:
                dados = supabase.table("ganhos").select("bruto", "liquido").execute()

                if not dados.data:
                    resposta.message("Nenhum registro encontrado.")
                else:
                    total_bruto = 0
                    total_liquido = 0

                    for item in dados.data:
                        bruto = item.get("bruto", 0)
                        liquido = item.get("liquido", 0)
                        total_bruto += bruto
                        total_liquido += liquido

                    texto_resposta = "\n🔢 Totais:\n"
                    texto_resposta += f"Bruto total: R$ {total_bruto:.2f}\n"
                    texto_resposta += f"Líquido total: R$ {total_liquido:.2f}"

                    resposta.message(texto_resposta)

            except Exception as erro:
                print(f"Erro ao buscar dados no Supabase: {erro}")
                resposta.message("Erro ao buscar os dados. Tente novamente mais tarde.")

            session["estado"] = "inicio"

        elif mensagem == "3":
            resposta.message("Bot encerrado. Até logo!")
            session.clear()

        else:
            resposta.message("Opção inválida. Digite 1, 2 ou 3.")

    elif session["estado"] == "aguardando_ganho":
        ganho = converter_para_float(mensagem)
        if ganho is not None:
            session["ganho"] = ganho
            resposta.message("Agora digite o valor gasto com combustível:")
            session["estado"] = "aguardando_combustivel"
        else:
            resposta.message("Por favor, envie um número válido. Ex: 100 ou 100.50")

    elif session["estado"] == "aguardando_combustivel":
        combustivel = converter_para_float(mensagem)
        if combustivel is not None:
            ganho = session.get("ganho", 0)
            liquido = ganho - combustivel

            try:
                resultado = supabase.table("ganhos").insert({
                    "bruto": ganho,
                    "liquido": liquido
                }).execute()
                print(f"Resposta do Supabase: {resultado}")
                #resposta.message(f"Seu ganho líquido hoje é: R$ {liquido:.2f}")
            except Exception as erro:
                print(f"Erro ao salvar no Supabase: {erro}")
                resposta.message("Erro ao salvar no banco. Tente novamente mais tarde.")

            session.clear()
        else:
            resposta.message("Por favor, envie um número válido para o combustível.")

    else:
        resposta.message("Erro inesperado. Vamos recomeçar.")
        session.clear()

    return str(resposta)

# ▶️ Inicialização do servidor Flask
if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=porta)
