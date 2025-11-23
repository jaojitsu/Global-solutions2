"""
Modelo simples de detecção de anomalias no consumo de energia.
"""

from pathlib import Path
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib

BASE_DIR = Path(__file__).resolve().parents[2]
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

def generate_energy_data(n=300):
    rng = np.random.default_rng(123)
    # padrão normal ~0.5 kWh com pouca variação
    normal = rng.normal(0.5, 0.1, size=n)
    # alguns picos
    anomalies = rng.normal(2.0, 0.2, size=15)
    data = np.concatenate([normal, anomalies])
    rng.shuffle(data)
    X = data.reshape(-1, 1)
    return X


def train_and_save():
    X = generate_energy_data()
    model = IsolationForest(contamination=0.05, random_state=123)
    model.fit(X)
    out_path = MODELS_DIR / "energy_anomaly.pkl"
    joblib.dump(model, out_path)
    print(f"Modelo de anomalia de energia salvo em {out_path}")


if __name__ == "__main__":
    train_and_save()
