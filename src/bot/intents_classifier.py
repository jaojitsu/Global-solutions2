"""
Classificador simples de intenção baseado em palavras-chave.
"""

from typing import Literal

Intent = Literal["checkin", "energia", "tarefas", "relatorio", "pandora", "outro"]


def classify_intent(text: str) -> Intent:
    t = text.lower()

    # Bem-estar / check-in
    if "checkin" in t or "como estou" in t or "bem estar" in t:
        return "checkin"

    # Energia / sustentabilidade
    if "energia" in t or "luz" in t or "kwh" in t:
        return "energia"

    # Tarefas / operações
    if "tarefas" in t or "to-do" in t or "prioridade" in t or "task" in t:
        return "tarefas"

    # Relatórios
    if "relatorio" in t or "relatório" in t or "report" in t:
        return "relatorio"

    # Saúde mental (Pandora) – textos mais emocionais
    if any(
        kw in t
        for kw in [
            "mental",
            "terapia",
            "triste",
            "tristeza",
            "deprimido",
            "depressivo",
            "ansioso",
            "ansiedade",
            "sem vontade",
            "sem energia",
            "esgotado",
            "sobrecarregado",
            "não vejo saída",
            "nao vejo saida",
        ]
    ):
        return "pandora"

    return "outro"
