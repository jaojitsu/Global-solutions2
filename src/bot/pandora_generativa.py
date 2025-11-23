# src/bot/pandora_generativa.py
"""
Pandora Generativa (Protótipo)
Versão conceitual que usaria um modelo generativo para respostas empáticas.
Não usada no projeto por questões de custo de inferência.
"""

from typing import Optional

SAFETY_PREFIX = """
Você é a Pandora, uma IA empática.
Nunca dê conselhos médicos.
Nunca encoraje comportamentos de risco.
Se detectar crise, mostre esta mensagem:

💛 Sinto muito que você esteja se sentindo assim.
Eu não posso oferecer ajuda de emergência.
Por favor, ligue 188 (CVV) ou procure atendimento profissional imediatamente.
"""

CRISIS = [
    "me matar", "suicidio", "suicídio", "tirar minha vida",
    "não quero mais viver", "kill myself", "suicide", "want to die"
]


def is_crisis(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in CRISIS)


def generate_with_llm(prompt: str) -> str:
    """
    Mock para chamada generativa.
    Aqui poderia entrar qualquer LLM:
    - OpenAI
    - HuggingFace
    - Mistral
    - Llama.cpp local
    - GPT4All
    """

    # EXEMPLO SIMBÓLICO
    # (retorna uma resposta fixa só para teste)
    return (
        "Compreendo. Parece que você está passando por algo importante. "
        "Se quiser, posso te ajudar a explorar seus sentimentos."
    )


def handle_pandora_generativa(user_id: str, text: str) -> str:
    # 1) Safety first
    if is_crisis(text):
        return (
            "💛 Sinto muito que você esteja se sentindo assim.\n\n"
            "Eu sou apenas um assistente virtual e **não posso oferecer ajuda de emergência**.\n"
            "No Brasil, ligue **188** (CVV)."
        )

    # 2) Monta prompt seguro
    prompt = SAFETY_PREFIX + "\nUsuário: " + text + "\nPandora:"

    # 3) Chama modelo generativo (placeholder)
    resposta = generate_with_llm(prompt)

    return resposta