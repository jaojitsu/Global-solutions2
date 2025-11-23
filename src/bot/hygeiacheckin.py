"""
Hygeia – agente de bem-estar (VERSÃO 3).

Agora:
- Pergunta o nome do colaborador antes do primeiro check-in;
- Guarda o nome em memória e usa nas respostas;
- Chama a API FastAPI /checkin para registrar no banco e calcular risco de estresse.
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict

import requests

from .intents_classifier import classify_intent

# ========= AJUSTE DE PATH =========
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# ========= CONFIG DA API =========
API_BASE_URL = os.getenv("HUMAN_OPS_API_URL", "http://localhost:8000")
CHECKIN_ENDPOINT = f"{API_BASE_URL}/checkin"

# ========= ESTADO EM MEMÓRIA =========
# Nome amigável por usuário (mapeia user_id -> nome)
USER_NAME: Dict[str, str] = {}

# Estado do fluxo de check-in por usuário
# Valores possíveis: "awaiting_name", "awaiting_scores", None
USER_STATE: Dict[str, Optional[str]] = {}


# ========= PROMPT / PERGUNTAS =========

CHECKIN_PROMPT = (
    "🧠 Vamos fazer um check-in rápido de bem-estar.\n\n"
    "Responda com **cinco números de 1 a 5**, separados por espaço ou vírgula, por exemplo: `3 2 4 4 5`.\n\n"
    "As perguntas são:\n"
    "1) Como está seu **sono** hoje?\n"
    "2) Você sente alguma **dor de cabeça**?\n"
    "3) Como você classifica seu **desempenho** recentemente?\n"
    "4) Como você diria que está a sua **carga de trabalho**?\n"
    "5) Quão **estressado(a)** você se sente?\n\n"
    "Envie as cinco notas de uma vez, na ordem acima. 🙂"
)


def _parse_scores(text: str) -> Optional[List[int]]:
    """
    Extrai números de 1 a 5 da mensagem do usuário.

    - Se encontrar 5 ou mais números -> usa os 5 primeiros (modelo completo).
    - Se encontrar apenas 3 números -> compatibilidade com formato antigo:
        [motivacao, cansaco, stress] -> [sono=3, dor=3, desempenho=mot, carga=cans, stress=stress]
    """
    nums = re.findall(r"[1-5]", text)
    if len(nums) >= 5:
        return list(map(int, nums[:5]))
    if len(nums) >= 3:
        mot, cans, stress = map(int, nums[:3])
        return [3, 3, mot, cans, stress]
    return None


def _call_checkin_api(user_id: str, scores: List[int]) -> Tuple[float, str]:
    """
    Chama a API /checkin passando as 5 respostas.

    Retorna:
        (risk_score, risk_level)
    """
    if len(scores) != 5:
        raise ValueError("Esperava 5 scores para o check-in.")

    sono, dor_cabeca, desempenho, carga_trabalho, stress = scores

    nome_colab = USER_NAME.get(user_id, user_id)

    payload = {
        "nome_colaborador": nome_colab,
        "sono": sono,
        "dor_cabeca": dor_cabeca,
        "desempenho": desempenho,
        "carga_trabalho": carga_trabalho,
        "stress": stress,
        "comentario": None,
    }

    resp = requests.post(CHECKIN_ENDPOINT, json=payload, timeout=5)
    resp.raise_for_status()
    data = resp.json()

    risk_score = float(data.get("risk_score", 0.0))
    risk_level = str(data.get("risk_level", "desconhecido"))
    return risk_score, risk_level


def handle_message(user_id: str, text: str) -> str:
    """
    Lógica principal da Hygeia com estados:

    - Estado None:
        * se intent == "checkin" -> pergunta o nome (se ainda não souber)
          ou já mostra o CHECKIN_PROMPT (se já souber).
    - Estado "awaiting_name":
        * qualquer texto é tratado como nome -> guarda e manda CHECKIN_PROMPT.
    - Estado "awaiting_scores":
        * tenta ler as notas -> chama API /checkin -> responde com risco.
    """
    t = text.strip()
    state = USER_STATE.get(user_id)
    intent = classify_intent(text)

    # ===== 1) Usuário disparou o comando "checkin" =====
    if intent == "checkin":
        # Se já conhecemos o nome, vamos direto pro formulário
        nome = USER_NAME.get(user_id)
        if nome:
            USER_STATE[user_id] = "awaiting_scores"
            return (
                f"{nome}, vamos fazer um check-in rápido de bem-estar. 💚\n\n"
                + CHECKIN_PROMPT
            )
        # Se ainda não conhecemos, pedir o nome primeiro
        USER_STATE[user_id] = "awaiting_name"
        return (
            "Antes de começarmos o check-in, como posso te chamar? 🙂\n\n"
            "Digite apenas o seu nome ou como prefere ser chamado (ex: `Jonas`)."
        )

    # ===== 2) Se estamos aguardando o nome =====
    if state == "awaiting_name":
        # Tudo que vier agora é considerado nome
        nome = t
        if len(nome) > 60:
            nome = nome[:60]
        USER_NAME[user_id] = nome
        USER_STATE[user_id] = "awaiting_scores"
        return (
            f"Prazer te conhecer, {nome}! 🙌\n\n"
            + "Agora, vamos ao check-in:\n\n"
            + CHECKIN_PROMPT
        )

    # ===== 3) Se estamos aguardando as notas =====
    if state == "awaiting_scores":
        scores = _parse_scores(t)
        if not scores:
            return (
                "Não consegui entender as notas. 🤔\n\n"
                "Envie **cinco números de 1 a 5**, separados por espaço ou vírgula, "
                "por exemplo: `3 2 4 4 5`."
            )

        sono, dor, desempenho, carga, stress = scores
        nome = USER_NAME.get(user_id)

        if nome:
            header = (
                f"Obrigado por compartilhar seu estado hoje, {nome} 🙏\n\n"
                f"**Sono:** {sono}\n"
                f"**Dor de cabeça:** {dor}\n"
                f"**Desempenho:** {desempenho}\n"
                f"**Carga de trabalho:** {carga}\n"
                f"**Stress:** {stress}\n\n"
            )
        else:
            header = (
                "Obrigado por compartilhar seu estado hoje 🙏\n\n"
                f"**Sono:** {sono}\n"
                f"**Dor de cabeça:** {dor}\n"
                f"**Desempenho:** {desempenho}\n"
                f"**Carga de trabalho:** {carga}\n"
                f"**Stress:** {stress}\n\n"
            )

        try:
            risk_score, risk_level = _call_checkin_api(user_id, scores)
            prob_pct = round(risk_score * 100)
        except Exception:
            # Não quebrar fluxo se a API falhar
            USER_STATE[user_id] = None
            return (
                header
                + "Tentei registrar seu check-in e avaliar o risco de estresse com o modelo interno, "
                "mas tive um problema ao acessar a API de bem-estar.\n\n"
                "Mesmo assim, é importante você cuidar de descanso, sono e limites. "
                "Se sentir que está sobrecarregado(a), vale conversar com alguém de confiança "
                "ou buscar apoio profissional. 💚"
            )

        # Zeramos o estado: check-in concluído
        USER_STATE[user_id] = None

        if risk_level == "alto":
            return (
                header
                + f"O modelo sinalizou **risco elevado de estresse** (aprox. {prob_pct}% de probabilidade).\n\n"
                "✨ Algumas sugestões:\n"
                "- Veja se consegue fazer pequenas pausas ao longo do dia;\n"
                "- Se possível, converse com alguém de confiança sobre como você está se sentindo;\n"
                "- Considere buscar apoio de um(a) profissional de saúde mental.\n\n"
                "⚠️ Se em algum momento você tiver pensamentos de se machucar "
                "ou de não querer mais viver,\n"
                "procure ajuda imediatamente. No Brasil, você pode ligar **188** (CVV) "
                "ou buscar um serviço de emergência na sua região.\n\n"
                "Posso te ajudar a acompanhar isso com novos check-ins ao longo da semana. 💛"
            )
        elif risk_level == "moderado":
            return (
                header
                + f"O modelo indicou um **nível moderado de estresse** (aprox. {prob_pct}%).\n\n"
                "Vale ficar atento(a) a sinais de cansaço acumulado e, se possível:\n"
                "- Ajustar a carga de trabalho;\n"
                "- Planejar momentos de descanso real (sono, lazer, desconexão de telas);\n"
                "- Conversar com liderança ou RH se sentir que a pressão está alta.\n\n"
                "Se em algum momento isso piorar ou você se sentir sobrecarregado(a), "
                "procure apoio. 💚"
            )
        else:  # "baixo" ou qualquer outro
            return (
                header
                + f"O modelo **não indicou risco alto de estresse** (aprox. {prob_pct}%).\n\n"
                "Mesmo assim, é sempre importante cuidar de sono, descanso e limites.\n"
                "Se quiser, posso te ajudar com novos check-ins ou com organização de tarefas "
                "pra evitar sobrecarga. 🙂"
            )

    # ===== 4) fallback: mensagem genérica da Hygeia =====
    return (
        "Sou a **Hygeia**, agente focada em bem-estar. 💚\n\n"
        "- Se você quiser fazer um check-in completo, basta digitar **`checkin`**.\n"
        "- Se for sua primeira vez, vou perguntar **como você prefere ser chamado(a)**.\n"
        "- Depois, me mande cinco notas (1–5) de sono, dor de cabeça, desempenho, "
        "carga de trabalho e stress, como `3 2 4 4 5`.\n"
        "- Eu vou registrar isso na API de bem-estar e calcular seu nível de estresse."
    )
