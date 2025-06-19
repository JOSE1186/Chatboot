from supabase import create_client

# Conexão com Supabase
url = "https://mbyuhxjbwmvbhpieywjm.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1ieXVoeGpid212YmhwaWV5d2ptIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTAxODM0ODAsImV4cCI6MjA2NTc1OTQ4MH0.TF2gFOBExvn9FXb_n8gII-6FGf_NUc1VYvqk6ElCXAM"
supabase = create_client(url, key)

print("Bot funcionando")

bruto = []
liquido1 = []

while True:
    qualquer_coisa = input("")
    if qualquer_coisa:
        print("Menu:")
        print("digite 1 para inserir o ganho de hoje")
        print("digite 2 para ver o saldo liquido e bruto")
        print("digite 3 para sair do bot")
        escolha = input("")
        if escolha == "1":
            valor_bruto = float(input("Digite o valor do ganho bruto: "))
            combustivel = float(input("Digite o valor dos gastos: "))
            liquido = valor_bruto - combustivel
            bruto.append(valor_bruto)
            liquido1.append(liquido)

            # SALVAR NO SUPABASE (sem interferir na lógica do bot)
            supabase.table("ganhos").insert({
                "bruto": valor_bruto,
                "liquido": liquido
            }).execute()

        elif escolha == "2":
            print("Saldo bruto: ", sum(bruto))
            print("Saldo liquido: ", sum(liquido1))
        elif escolha == "3":
            print("Bot encerrado")
            break
        else:
            print("Opção inválida. Tente novamente.")
