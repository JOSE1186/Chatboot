from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
from supabase import create_client, Client

app = Flask(__name__)

# Ler URL e chave anon do Supabase das variáveis de ambiente
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise Exception("Faltando SUPABASE_URL ou SUPABASE_ANON_KEY nas variáveis de ambiente")

# Criar cliente Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

@app.route("/")
def home():
    return "Bot está ativo no Render!"

@app.route("/sms", methods=["POST"])
def sms_reply():
    numero = request.form.get("From")
    msg = request.form.get("Body").strip().lower()

    resp = MessagingResponse()

    if msg == "1":
        resp.message("Qual foi o ganho de hoje? Envie no formato: ganho:100.00")

    elif msg.startswith("ganho:"):
        try:
            valor = float(msg.split(":")[1])
            supabase.table("ganhos_combustiveis").insert({
                "numero": numero,
                "ganho": valor,
                "combustivel": 0.0  # combustível ainda não registrado
            }).execute()
            resp.message("Ganho registrado! Agora envie o combustível no formato: combustivel:30.00")
        except:
            resp.message("Formato inválido. Use: ganho:100.00")

    elif msg.startswith("combustivel:"):
        try:
            valor = float(msg.split(":")[1])
            dados = supabase.table("ganhos_combustiveis") \
                .select("*") \
                .eq("numero", numero) \
                .eq("combustivel", 0.0) \
                .order("id", desc=True) \
                .limit(1).execute()
            registros = dados.data
            if registros:
                registro = registros[0]
                supabase.table("ganhos_combustiveis").update({
                    "combustivel": valor
                }).eq("id", registro["id"]).execute()
                liquido = registro["ganho"] - valor
                resp.message(f"Combustível registrado!\nLucro líquido do dia: R$ {liquido:.2f}")
            else:
                resp.message("Não foi encontrado ganho pendente para associar o combustível. Envie primeiro o ganho.")
        except:
            resp.message("Formato inválido. Use: combustivel:30.00")

    elif msg == "2":
        dados = supabase.table("ganhos_combustiveis") \
            .select("*") \
            .eq("numero", numero) \
            .execute()
        registros = dados.data

        if registros:
            total_bruto = sum(r["ganho"] for r in registros)
            total_combustivel = sum(r["combustivel"] for r in registros)
            total_liquido = total_bruto - total_combustivel

            resposta = (
                f"Total bruto: R$ {total_bruto:.2f}\n"
                f"Total combustível: R$ {total_combustivel:.2f}\n"
                f"Total líquido: R$ {total_liquido:.2f}"
            )
            resp.message(resposta)
        else:
            resp.message("Nenhum dado encontrado para seu número.")

    else:
        resp.message("Opção inválida. Envie '1' para registrar ganho, '2' para totalizar.")

    return str(resp)


if __name__ == "__main__":
    app.run(debug=True)
