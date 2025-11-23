import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "config" / "db" / "human_ops.db"
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.core.orchestrator import route_message

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn


st.set_page_config(
    page_title="HUM.A.N OPS Dashboard",
    layout="wide",
)

with st.sidebar:
    st.markdown("### 🤖 Copiloto")

    if "show_chat" not in st.session_state:
        st.session_state["show_chat"] = False

    label = "Abrir chat" if not st.session_state["show_chat"] else "Fechar chat"
    if st.button(label):
        st.session_state["show_chat"] = not st.session_state["show_chat"]

    st.caption("Use o copiloto para tirar dúvidas rápidas: `ajuda`, `checkin`, `tarefas`...")

st.title("🌱 HUM.A.N OPS – Human-Aware & Sustainable Operations")

tabs = st.tabs(
    ["👤 Pessoas", "⚙️ Operações", "🌍 Sustentabilidade", "🤝 Inclusão","🤖 Copiloto – Chat Bot"]
)

# ============ PESSOAS ============
with tabs[0]:
    st.subheader("Pulso de Bem-Estar")
    conn = get_connection()
    df_checkin = pd.read_sql_query(
        """
        SELECT c.nm_colaborador,
               ch.dt,
               ch.q1 AS motivacao,
               ch.q2 AS cansaco,
               ch.q3 AS stress
        FROM checkin ch
        JOIN colaborador c ON c.id_colab = ch.id_colab
        ORDER BY ch.dt DESC
        LIMIT 100
        """,
        conn,
    )

    if df_checkin.empty:
        st.info("Ainda não há check-ins registrados.")
    else:
        st.dataframe(df_checkin)

        st.line_chart(
            df_checkin.sort_values("dt").set_index("dt")[
                ["motivacao", "cansaco", "stress"]
            ]
        )

    conn.close()

# ============ OPERAÇÕES ============
with tabs[1]:
    st.subheader("Automação de Tarefas e Carga de Trabalho")
    st.write("Exemplo de visão de tarefas por colaborador (dados simulados).")
    # Placeholder – você pode ligar na tabela tarefa
    sample = pd.DataFrame(
        {
            "colaborador": ["Ana", "Bruno", "Carla", "Diego"],
            "tarefas_hoje": [5, 8, 3, 10],
            "horas_estimada": [4, 6, 2, 7],
        }
    )
    st.bar_chart(sample.set_index("colaborador")["tarefas_hoje"])

# ============ SUSTENTABILIDADE ============
with tabs[2]:
    st.subheader("Consumo de Energia (kWh)")
    conn = get_connection()
    df_energy = pd.read_sql_query(
        """
        SELECT dt, kwh, equipamento, local
        FROM energia
        ORDER BY dt DESC
        LIMIT 200
        """,
        conn,
    )
    if df_energy.empty:
        st.info("Sem leituras de energia.")
    else:
        st.dataframe(df_energy)
        st.line_chart(df_energy.sort_values("dt").set_index("dt")["kwh"])
    conn.close()

# ============ INCLUSÃO ============
with tabs[3]:
    st.subheader("Indicadores de Inclusão (dados simulados)")
    st.write(
        "Nesta aba, serão mostradas métricas de fairness, aprovação por grupo, etc."
    )
    df_inclusao = pd.DataFrame(
        {
            "grupo": ["Grupo A", "Grupo B"],
            "taxa_aprovacao": [0.65, 0.52],
        }
    )
    st.bar_chart(df_inclusao.set_index("grupo")["taxa_aprovacao"])
    st.caption("Exemplo de diferença de taxa de aprovação entre grupos.")


# ================= COPILOTO – CHAT BOT =================
if st.session_state.get("show_chat", False):
    st.markdown("---")
    st.subheader("🤖 Copiloto – Chat Bot")

    if "bot_history" not in st.session_state:
        st.session_state.bot_history = []

    # mostra o histórico
    for role, msg in st.session_state.bot_history:
        with st.chat_message(role):
            st.markdown(msg)

    # entrada de texto
    user_msg = st.chat_input("Digite sua mensagem...")

    if user_msg:
        # mensagem do usuário
        st.session_state.bot_history.append(("user", user_msg))
        with st.chat_message("user"):
            st.markdown(user_msg)

        # resposta do bot (route_message já importado no topo)
        bot_reply = route_message("dashboard_user", user_msg)
        st.session_state.bot_history.append(("assistant", bot_reply))
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
