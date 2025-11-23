"""
Simulador simples de leituras de energia gravando na tabela energia.
Roda em loop ou cron para gerar dados.
"""

import time
import random
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "config" / "db" / "human_ops.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def insert_energy(kwh: float, equipamento: str = "Servidor", local: str = "Sala 1"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO energia (dt, kwh, equipamento, local, cd_area)
        VALUES (datetime('now'), ?, ?, ?, 1)
        """,
        (kwh, equipamento, local),
    )
    conn.commit()
    conn.close()

def main(loop: bool = False):
    while True:
        base = 0.4
        noise = random.uniform(-0.05, 0.1)
        spike = random.random() < 0.05
        kwh = base + noise + (1.5 if spike else 0)
        insert_energy(kwh)
        print(f"Inserido kWh={kwh:.3f}")
        if not loop:
            break
        time.sleep(30)

if __name__ == "__main__":
    main(loop=True)
