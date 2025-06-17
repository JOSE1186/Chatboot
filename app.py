from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
from supabase import create_client, Client

app = Flask(__name__)

# --- Defina suas variáveis aqui diretamente para teste ---

SUPABASE_URL = "https://mbyuhxjbwmvbhpieywjm.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ieXVoeGpid212YmhwaWV5d2ptIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAxODM0ODAsImV4cCI6MjA2NTc1OTQ4MH0.TF2gFOBExvn9FXb_n8gII-6FGf_NUc1VYvqk6ElCXAM"

# Se quiser usar as variáveis do ambiente, substitua acima por:
# SUPABASE_URL = os.environ.get("SUPABASE_URL")
# SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise Exception("Faltando SUPABASE_URL ou SUPABASE_ANON_KEY nas variáveis de ambiente")

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
                "combustivel": 0.0
            }).execute()
            resp.message("Ganho registrado! Agora envie o combustível no formato: combustivel:30.00")
        except:
            resp.message("Formato inválido. Use: ganho:100.00")
    elif msg.startswith("combustivel:"):
        try:
            valor = float(msg.split(":")[1])
            dados = supabase.table("ganhos_combustiveis")\
                .select("*")\
                .eq("numero", numero)\
                .eq("combustivel", 0.0)\
                .order("id", desc=True)\
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
        # Calcular totais para o usuário
        dados = supabase.table("ganhos_combustiveis")\
            .select("*")\
            .eq("numero", numero).execute()
        registros = dados.data
        total_ganho = sum(r["ganho"] for r in registros)
        total_combustivel = sum(r["combustivel"] for r in registros)
        total_liquido = total_ganho - total_combustivel
        resp.message(
            f"Totais até agora:\nGanho: R$ {total_ganho:.2f}\n"
            f"Combustível: R$ {total_combustivel:.2f}\n"
            f"Lucro Líquido: R$ {total_liquido:.2f}"
        )
    else:
        resp.message("Comando inválido.\nEnvie:\n1 para registrar ganho\n2 para ver totais")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
