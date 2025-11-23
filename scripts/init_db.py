"""
Script de inicialização do projeto HUM.A.N OPS.

O que ele faz:
1) Cria o arquivo de banco de dados SQLite (human_ops.db) em config/db/
2) Executa o schema.sql (criação das tabelas)
3) Executa o seeds.sql (dados iniciais)
4) Treina e salva os modelos de ML (stress_model.pkl e energy_anomaly.pkl)

Rodar com:
    python scripts/init_db.py
"""

from pathlib import Path
import sqlite3
import sys

# ========= Paths básicos =========

# scripts/ -> root do projeto
BASE_DIR = Path(__file__).resolve().parents[1]

CONFIG_DB_DIR = BASE_DIR / "config" / "db"
SCHEMA_PATH = CONFIG_DB_DIR / "schema.sql"
SEEDS_PATH = CONFIG_DB_DIR / "seeds.sql"
DB_PATH = CONFIG_DB_DIR / "human_ops.db"

# Adiciona o root no sys.path pra importar src.*
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))


def run_sql_script(conn: sqlite3.Connection, path: Path, label: str):
    if not path.exists():
        raise FileNotFoundError(f"[ERRO] Arquivo {label} não encontrado em {path}")
    with path.open("r", encoding="utf-8") as f:
        sql = f.read()
    conn.executescript(sql)


def init_database():
    print(f"📁 Base do projeto: {BASE_DIR}")
    print(f"💾 Banco de dados: {DB_PATH}")

    CONFIG_DB_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    # garante FK no SQLite
    conn.execute("PRAGMA foreign_keys = ON;")

    # schema
    print("🧱 Executando schema.sql ...")
    run_sql_script(conn, SCHEMA_PATH, "schema.sql")

    # seeds
    print("🌱 Executando seeds.sql ...")
    run_sql_script(conn, SEEDS_PATH, "seeds.sql")

    conn.commit()
    conn.close()
    print("✅ Banco criado e populado com sucesso.\n")


def train_models():
    print("🧠 Treinando modelos de ML...")

    # importa aqui pra usar o sys.path já ajustado
    from src.ml.stress_model import train_and_save as train_stress
    from src.ml.energy_anomaly import train_and_save as train_energy

    train_stress()
    train_energy()

    print("✅ Modelos treinados e salvos em /models.\n")


def main():
    print("🚀 Iniciando setup do HUM.A.N OPS")
    init_database()
    train_models()
    print("🎉 Setup concluído. API e Dashboard já podem usar o banco e os modelos.")


if __name__ == "__main__":
    main()
