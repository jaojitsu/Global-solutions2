from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import joblib
import os
import sqlite3
from pathlib import Path

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("human_ops_api")

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "config" / "db" / "human_ops.db"
MODELS_DIR = BASE_DIR / "models"

app = FastAPI(
    title="HUM.A.N OPS API",
    description="API para bem-estar, produtividade, sustentabilidade e inclusão.",
    version="0.2.0",
)

# ==== MODELOS Pydantic ====


class CheckinRequest(BaseModel):
    # Identificação do colaborador
    colaborador_id: Optional[int] = None
    nome_colaborador: Optional[str] = None

    # Perguntas 1–5 (escala 1–5)
    sono: int  # 1) Como está seu sono?
    dor_cabeca: int  # 2) Você sente alguma dor de cabeça?
    desempenho: int  # 3) Como você classifica seu desempenho?
    carga_trabalho: int  # 4) Como você diria que está a sua carga de trabalho?
    stress: int  # 5) Quão estressado você se sente?

    comentario: Optional[str] = None


class StressScoreResponse(BaseModel):
    risk_score: float
    risk_level: str


class EnergyStatusResponse(BaseModel):
    current_kwh: float
    daily_total: float
    anomaly_flag: bool


# ==== HELPERS de BD ====


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_or_create_colaborador(nome: str) -> int:
    """
    Dado um nome, retorna id_colab.
    Se não existir, cria um novo colaborador.
    """
    nome = nome.strip()
    if not nome:
        raise HTTPException(
            status_code=400,
            detail="Nome do colaborador vazio. Informe 'nome_colaborador' válido.",
        )

    conn = get_connection()
    cur = conn.cursor()

    # tentar encontrar pelo nome exato
    cur.execute(
        "SELECT id_colab FROM colaborador WHERE nm_colaborador = ?",
        (nome,),
    )
    row = cur.fetchone()
    if row:
        conn.close()
        return int(row["id_colab"])

    # se não achar, cria
    cur.execute(
        "INSERT INTO colaborador (nm_colaborador) VALUES (?)",
        (nome,),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    logger.info("Criado novo colaborador '%s' com id %s", nome, new_id)
    return int(new_id)


# ==== Carregar modelos (se existirem) ====


def load_model(path: Path):
    if path.exists():
        return joblib.load(path)
    logger.warning("Modelo não encontrado em %s, usando fallback.", path)
    return None


STRESS_MODEL = load_model(MODELS_DIR / "stress_model.pkl")
ENERGY_MODEL = load_model(MODELS_DIR / "energy_anomaly.pkl")


# ==== ROTAS ====


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "HUM.A.N OPS API rodando."}


@app.post("/checkin", response_model=StressScoreResponse)
def criar_checkin(payload: CheckinRequest):
    """
    Cria um check-in de bem-estar (Hygeia) e calcula risco de estresse.

    - Aceita 'colaborador_id' ou 'nome_colaborador'.
    - Usa 5 perguntas (sono, dor de cabeça, desempenho, carga, stress).
    - Calcula 'risk_score' com modelo de ML (LogisticRegression) se disponível.
    - Grava q1..q5 + stress_score na tabela 'checkin'.
    """

    # ===== 1) Resolver colaborador =====
    if payload.colaborador_id is not None:
        colab_id = payload.colaborador_id
    elif payload.nome_colaborador:
        colab_id = get_or_create_colaborador(payload.nome_colaborador)
    else:
        raise HTTPException(
            status_code=400,
            detail="Informe 'colaborador_id' ou 'nome_colaborador' para registrar o check-in.",
        )

    # ===== 2) Montar features para o modelo =====
    features = [
        payload.sono,
        payload.dor_cabeca,
        payload.desempenho,
        payload.carga_trabalho,
        payload.stress,
    ]

    # ===== 3) Calcular probabilidade de risco =====
    if STRESS_MODEL is not None:
        import numpy as np

        proba = float(STRESS_MODEL.predict([features])[0])
        proba = max(0.0, min(1.0, proba))
    else:
        # fallback simples: média normalizada de carga_trabalho + stress
        proba = (payload.carga_trabalho + payload.stress) / 10.0
    stress_score = float(round(proba, 3))

    if proba < 0.33:
        level = "baixo"
    elif proba < 0.66:
        level = "moderado"
    else:
        level = "alto"

    # ===== 4) Gravar no banco =====
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO checkin (
            id_colab,
            dt,
            q1, q2, q3, q4, q5,
            texto_opcional,
            stress_score
        )
        VALUES (
            ?, datetime('now'),
            ?, ?, ?, ?, ?,
            ?, ?
        )
        """,
        (
            colab_id,
            payload.sono,
            payload.dor_cabeca,
            payload.desempenho,
            payload.carga_trabalho,
            payload.stress,
            payload.comentario,
            stress_score,
        ),
    )
    conn.commit()
    conn.close()

    logger.info(
        "Check-in registrado para colaborador %s, risco %.3f (%s)",
        colab_id,
        stress_score,
        level,
    )

    return StressScoreResponse(risk_score=stress_score, risk_level=level)


@app.get("/energia/status", response_model=EnergyStatusResponse)
def energia_status():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT kwh, dt
        FROM energia
        ORDER BY dt DESC
        LIMIT 1
        """
    )
    row = cur.fetchone()

    if not row:
        conn.close()
        return EnergyStatusResponse(
            current_kwh=0.0, daily_total=0.0, anomaly_flag=False
        )

    current_kwh = float(row["kwh"])

    cur.execute(
        """
        SELECT SUM(kwh) as total
        FROM energia
        WHERE date(dt) = date('now')
        """
    )
    total_row = cur.fetchone()
    daily_total = float(total_row["total"] or 0.0)

    # Usa modelo se existir, senão regra simples
    anomaly_flag = False
    if ENERGY_MODEL is not None:
        import numpy as np

        pred = ENERGY_MODEL.predict([[current_kwh]])
        anomaly_flag = bool(pred[0] == -1)
    else:
        anomaly_flag = current_kwh > 2.0  # exemplo hardcoded

    conn.close()
    return EnergyStatusResponse(
        current_kwh=current_kwh,
        daily_total=daily_total,
        anomaly_flag=anomaly_flag,
    )
