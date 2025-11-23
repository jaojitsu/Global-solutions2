"""
Orquestrador que decide qual agente responde: Atena, Hygeia, Gaia, Sophia, Pandora.
"""

from typing import Literal
from src.bot import atenabot, hygeiacheckin, pandora
from src.bot.intents_classifier import classify_intent


# Contexto simples em memória (por usuário)
USER_CONTEXT = {}

Agent = Literal["atena", "hygeia", "gaia", "sophia", "pandora"]

HELP_TEXT = (
    "📘 **Comandos disponíveis:**\n"
    "- `checkin` – iniciar check-in de bem-estar (Hygeia)\n"
    "- `tarefas` – dicas e automações de trabalho (Atena)\n"
    "- `relatorio` – resumo automático (Atena)\n"
    "- `energia` – informações de sustentabilidade (Gaia)\n"
    "- `inclusao` – métricas de fairness (Sophia)\n"
    "- `falar` – conversar em modo Pandora (saúde mental)\n"
    "- `ajuda` – mostrar esta lista\n"
    "- `sair` – encerrar bate-papo\n"
)


def route_message(user_id: str, text: str) -> str:
    raw_text = text.strip()
    t = raw_text.lower()
    current_mode = USER_CONTEXT.get(user_id)

    # ========= 0) Se usuário já está em modo Pandora =========
    if current_mode == "pandora":
        # comandos para sair da Pandora
        if t in ["sair", "sair pandora", "voltar", "menu"]:
            USER_CONTEXT[user_id] = None
            return "Saindo do modo Pandora. Se quiser ver os comandos gerais, digite `ajuda`."
        # qualquer outra coisa: mandar pra Pandora
        return pandora.handle_pandora_message(user_id, raw_text)

    # ========= 1) Comandos globais =========
    if t in ["ajuda", "help"]:
        return HELP_TEXT

    if t in ["sair", "exit", "quit"]:
        return "Até mais! 👋 Se precisar de mim de novo, é só digitar algo."

    if t in ["voltar", "menu"]:
        return "Voltando ao menu principal...\n\n" + HELP_TEXT

    # ========= 2) Entrar em modo Pandora sem prefixo especial =========
    if t in [
        "falar",
        "quero conversar",
        "preciso conversar",
        "preciso desabafar",
        "pandora",
    ]:
        USER_CONTEXT[user_id] = "pandora"
        return (
            "💬 Você está agora falando com a **Pandora**, IA focada em saúde mental.\n\n"
            "Pode me contar, com suas palavras, o que está acontecendo. "
            "Se em algum momento algo parecer muito pesado, eu também vou te orientar "
            "a buscar ajuda humana e profissional. 💛"
        )

    # (Opcional) manter compat com prefixo 'mental' / 'terapia'
    if t.startswith("mental") or t.startswith("terapia"):
        USER_CONTEXT[user_id] = "pandora"
        return pandora.handle_pandora_message(user_id, raw_text)

    # ========= 3) Fluxo de check-in (Hygeia) =========
    if current_mode == "checkin":
        reply = hygeiacheckin.handle_message(user_id, raw_text)
        # se o check-in foi concluído, limpamos o contexto
        if "Obrigado por compartilhar seu estado" in reply:
            USER_CONTEXT[user_id] = None
        return reply

    # classificador de intenção
    intent = classify_intent(raw_text)

    if intent == "checkin":
        USER_CONTEXT[user_id] = "checkin"
        return hygeiacheckin.handle_message(user_id, raw_text)

    # ========= 4) Atena – tarefas/relatórios =========
    if intent in ("tarefas", "relatorio"):
        return atenabot.handle_message(user_id, raw_text)

    # ========= 5) Pandora via intenção emocional =========
    if intent == "pandora":
        USER_CONTEXT[user_id] = "pandora"
        return pandora.handle_pandora_message(user_id, raw_text)

    # ========= 6) Gaia / Sophia placeholders =========
    if intent == "energia":
        return "🌍 Gaia aqui! Em breve mostrarei insights de energia pelo bot — use o dashboard enquanto isso."

    if intent == "inclusao":
        return "🤝 Sophia aqui! Em breve responderei análises de fairness também."

    # ========= 7) fallback =========
    return (
        "🤖 Não entendi direito...\n\n"
        "Eu sou o Copiloto HUM.A.N OPS e posso te ajudar com:\n"
        "- Bem-estar e **saúde mental** (Hygeia + Pandora)\n"
        "- Produtividade e **tarefas/relatórios** (Atena)\n"
        "- **Energia** e sustentabilidade (Gaia)\n"
        "- **Inclusão** e fairness (Sophia)\n\n"
        "Digite `ajuda` para ver os comandos."
    )
