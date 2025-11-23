"""
AtenaBot – foco em produtividade, tarefas e relatórios.
"""

from .intents_classifier import classify_intent

def handle_message(user_id: str, text: str) -> str:
    intent = classify_intent(text)
    if intent == "tarefas":
        return (
            "📋 Atena aqui! Posso te ajudar a priorizar as tarefas.\n"
            "- Exemplo: focar nas 3 com maior impacto e prazo mais próximo.\n"
            "(Na versão completa, eu leria suas tarefas reais do sistema.)"
        )
    if intent == "relatorio":
        return (
            "📊 Posso montar um resumo automático do dia com base nos dados "
            "de tarefas, check-ins e energia.\n"
            "(Na POC, você verá isso no dashboard Streamlit.)"
        )
    return "Sou a Atena, focada em produtividade. Tenta falar de tarefas ou relatórios 😉"
