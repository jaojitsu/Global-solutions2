"""
Treino de um modelo contínuo de risco de estresse usando dados simulados
do CSV 'Fatores de Estresse.csv'.

Perguntas (1–5):
1) Como está seu sono?
2) Você sente alguma dor de cabeça?
3) Como você classifica seu desempenho?
4) Como você diria que está a sua carga de trabalho?
5) Quão estressado você se sente?

Saída: risk_score contínuo entre 0 e 1.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib

BASE_DIR = Path(__file__).resolve().parents[2]
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

DATA_PATH = BASE_DIR  / "Fatores de Estresse.csv"


def load_stress_csv():
    """
    Lê o CSV original (1 coluna com '3,1,3,2,3' etc.)
    e retorna um array N x 5 com inteiros 1–5.
    """
    df = pd.read_csv(DATA_PATH, encoding="latin1", sep=";")
    col = df.columns[0]
    values = df[col].astype(str).str.split(",", expand=True)

    if values.shape[1] != 5:
        raise ValueError(
            f"Esperava 5 colunas de respostas, mas encontrei {values.shape[1]}."
        )

    X = values.astype(int).values
    return X


def build_targets(X: np.ndarray) -> np.ndarray:
    """
    Cria um risco contínuo entre 0 e 1 a partir das 5 respostas.

    Heurística:
      - Sono ruim aumenta risco
      - Dor de cabeça aumenta risco
      - Desempenho ruim aumenta risco
      - Carga de trabalho alta aumenta risco
      - Stress alto aumenta risco

    Cada componente é normalizado entre 0 e 1 e fazemos uma média ponderada.
    """

    sono = X[:, 0]            # 1 = péssimo sono, 5 = ótimo
    dor_cabeca = X[:, 1]      # 1 = nada, 5 = muita dor
    desempenho = X[:, 2]      # 1 = péssimo, 5 = ótimo
    carga_trabalho = X[:, 3]  # 1 = pouca, 5 = muita
    stress = X[:, 4]          # 1 = pouco, 5 = muito

    # Normalizar para 0–1 de "ruim" pra "bom"
    # Para risco, queremos o "ruim":
    risco_sono = (6 - sono) / 5.0          # sono baixo => risco alto
    risco_dor = dor_cabeca / 5.0           # mais dor => mais risco
    risco_desempenho = (6 - desempenho) / 5.0
    risco_carga = carga_trabalho / 5.0
    risco_stress = stress / 5.0

    # Peso igual pra cada componente (poderia ajustar depois)
    risk_raw = (
        risco_sono
        + risco_dor
        + risco_desempenho
        + risco_carga
        + risco_stress
    ) / 5.0

    # Garante que está entre 0 e 1
    risk_raw = np.clip(risk_raw, 0.0, 1.0)
    return risk_raw


def train_and_save():
    X = load_stress_csv()
    y = build_targets(X)  # valores contínuos 0–1

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
    )
    model.fit(X, y)

    out_path = MODELS_DIR / "stress_model.pkl"
    joblib.dump(model, out_path)
    print(f"Modelo de estresse salvo em {out_path}")
    print("Risco médio no dataset:", float(y.mean()))


if __name__ == "__main__":
    train_and_save()
