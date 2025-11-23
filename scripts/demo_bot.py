from src.core.orchestrator import route_message

print("=== HUM.A.N OPS – Demonstração do Bot ===\n")

while True:
    user = input("Você: ")
    if user.lower() in ["sair", "exit", "quit"]:
        print("Encerrando demo...")
        break

    resposta = route_message("user123", user)
    print("Bot:", resposta, "\n")
