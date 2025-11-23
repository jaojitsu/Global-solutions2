import json
import random
from pathlib import Path

from src.ml.pandora_nlu import predict_intent

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "intents.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    INTENTS = json.load(f)["intents"]


def find_responses(tag: str):
    for intent in INTENTS:
        if intent["tag"] == tag:
            return intent.get("responses", [])
    return []


# Palavras/expressões de risco (EN + PT-BR)
CRISIS_KEYWORDS = [
    # inglês
    "kill myself",
    "want to die",
    "suicide",
    "end my life",
    "i don't want to live",
    "self harm",
    # português
    "me matar",
    "me machucar",
    "não quero mais viver",
    "nao quero mais viver",
    "não aguento mais viver",
    "nao aguento mais viver",
    "tirar minha vida",
    "acabar com tudo",
    "acabar com a minha vida",
    "vida não vale",
    "vida nao vale",
]


def is_crisis(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in CRISIS_KEYWORDS)


def _clean_prefix(text: str) -> str:
    """
    Remove prefixos 'mental' ou 'terapia' para não atrapalhar o modelo/intents.
    """
    t = text.strip()
    for prefix in ("mental ", "terapia "):
        if t.lower().startswith(prefix):
            return t[len(prefix):].strip()
    return t


def handle_pandora_message(user_id: str, text: str) -> str:
    """
    IA conversacional para saúde mental (Pandora).
    Usa modelo de intents + respostas definidas em intents.json.
    """
    # remove 'mental ' / 'terapia ' do começo, se tiver
    cleaned_text = _clean_prefix(text)

    # 1) Checagem de crise
    if is_crisis(cleaned_text):
        return (
            "💛 Sinto muito que você esteja se sentindo assim.\n\n"
            "Eu sou apenas um assistente virtual e **não posso oferecer ajuda de emergência**, "
            "mas a sua vida é muito importante.\n\n"
            "Se você estiver em perigo imediato, procure ajuda emergencial na sua região.\n"
            "No Brasil, você também pode ligar **188** para o Centro de Valorização da Vida (CVV), "
            "que oferece apoio emocional 24h por dia, ou buscar atendimento em um serviço de saúde.\n\n"
            "Você não está sozinho. 💛"
        )

    # 2) Classificação de intenção
    tag, prob = predict_intent(cleaned_text)
    responses = find_responses(tag)

    # 3) Se o modelo estiver inseguro ou não tiver respostas, manda uma mensagem neutra em PT-BR
    if prob < 0.15 or not responses:
        return (
            "Entendo que você está passando por um momento difícil.\n\n"
            "Posso te ouvir e refletir com você sobre isso. "
            "Se quiser, pode me contar um pouco mais sobre o que está acontecendo?"
        )

    # 4) Caso normal: usar uma das respostas do intents.json
    return random.choice(responses)
