import sqlite3
from pathlib import Path
import sys

import pandas as pd
from dash import Dash, html, dcc, dash_table, Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import dash  

# ================== PATHS E IMPORTS ==================
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "config" / "db" / "human_ops.db"
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.core.orchestrator import route_message


def get_connection():
    return sqlite3.connect(DB_PATH)


# ================== MENSAGEM INICIAL DO BOT ==================
# Puxa automaticamente o HELP_TEXT do orchestrator
INITIAL_BOT_MSG = route_message("dashboard_user", "ajuda")


# ================== APP DASH ==================
app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server
app.title = "HUM.A.N OPS Dashboard"

app.layout = html.Div(
    style={"margin": "20px"},
    children=[
        # estado do chat (histórico + aberto/fechado)
        dcc.Store(
            id="chat-history",
            data=[
                {
                    "role": "assistant",
                    "message": INITIAL_BOT_MSG,
                }
            ],
        ),
        dcc.Store(id="chat-open", data=False),

        html.H1("🌱 HUM.A.N OPS – Human-Aware & Sustainable Operations"),

        dcc.Tabs(
            id="tabs",
            value="tab-pessoas",
            children=[
                dcc.Tab(label="👤 Pessoas", value="tab-pessoas"),
                dcc.Tab(label="⚙️ Operações", value="tab-operacoes"),
                dcc.Tab(label="🌍 Sustentabilidade", value="tab-sustentabilidade"),
                dcc.Tab(label="🤝 Inclusão", value="tab-inclusao"),
            ],
        ),
        html.Div(id="tabs-content", style={"marginTop": "20px"}),

        # ====== Botão flutuante do copiloto ======
        html.Button(
            "🤖",
            id="open-chat-btn",
            n_clicks=0,
            title="Abrir Copiloto",
            style={
                "position": "fixed",
                "bottom": "20px",
                "right": "50px",
                "width": "60px",
                "height": "60px",
                "borderRadius": "50%",
                "fontSize": "28px",
                "border": "none",
                "boxShadow": "0 4px 12px rgba(0,0,0,0.3)",
                "cursor": "pointer",
                "backgroundColor": "#6f42c1",
                "color": "white",
                "zIndex": 1000,
            },
        ),

        # ====== Janela do chat ======
        html.Div(
            id="chat-container",
            style={"display": "none"},
            children=[
                html.Div(
                    style={
                        "display": "flex",
                        "flexDirection": "column",
                        "height": "100%",
                    },
                    children=[
                        # Cabeçalho da janelinha
                        html.Div(
                            style={
                                "display": "flex",
                                "alignItems": "center",
                                "gap": "8px",
                                "marginBottom": "8px",
                                "borderBottom": "1px solid #e0e0e0",
                                "paddingBottom": "4px",
                            },
                            children=[
                                html.Span("🤖", style={"fontSize": "24px"}),
                                html.H3(
                                    "Copiloto – Chat Bot",
                                    style={"margin": 0, "fontSize": "18px"},
                                ),
                            ],
                        ),
                        # Área das mensagens
                        html.Div(
                            id="chat-messages",
                            style={
                                "borderRadius": "8px",
                                "padding": "8px",
                                "height": "340px",
                                "overflowY": "auto",
                                "backgroundColor": "#fafafa",
                                "border": "1px solid #e0e0e0",
                                "marginBottom": "8px",
                            },
                        ),
                        # Input + botão enviar
                        html.Div(
                            style={
                                "display": "flex",
                                "marginTop": "4px",
                                "gap": "8px",
                            },
                            children=[
                                dcc.Input(
                                    id="chat-input",
                                    placeholder="Digite sua mensagem...",
                                    type="text",
                                    style={
                                        "flex": 1,
                                        "height": "40px",
                                        "padding": "8px",
                                        "borderRadius": "8px",
                                        "border": "1px solid #ccc",
                                    },
                                ),
                                html.Button(
                                    "Enviar",
                                    id="send-button",
                                    n_clicks=0,
                                    style={
                                        "width": "90px",
                                        "borderRadius": "8px",
                                        "border": "1px solid #6f42c1",
                                        "backgroundColor": "#f5f0ff",
                                        "cursor": "pointer",
                                    },
                                ),
                            ],
                        ),
                        html.Small(
                            "Dicas: `ajuda`, `checkin`, `tarefas`, `falar`...",
                            style={"marginTop": "4px", "color": "#555"},
                        ),
                    ],
                )
            ],
        ),
    ],
)

# ================== CALLBACK TABS ==================
@app.callback(
    Output("tabs-content", "children"),
    Input("tabs", "value"),
)
def render_tab_content(tab):
    if tab == "tab-pessoas":
        return pessoas_layout()
    elif tab == "tab-operacoes":
        return operacoes_layout()
    elif tab == "tab-sustentabilidade":
        return sustentabilidade_layout()
    elif tab == "tab-inclusao":
        return inclusao_layout()
    return html.Div("Aba inválida.")


# ================== LAYOUTS DAS ABAS ==================
def pessoas_layout():
    conn = get_connection()
    df_checkin = pd.read_sql_query(
        """
        SELECT c.nm_colaborador,
               ch.dt,
               ch.q1 AS motivacao,
               ch.q2 AS cansaco,
               ch.q4 AS carga_trabalho,
               ch.q5 AS stress,
               ch.stress_score
        FROM checkin ch
        JOIN colaborador c ON c.id_colab = ch.id_colab
        ORDER BY ch.dt DESC
        LIMIT 100
        """,
        conn,
    )
    conn.close()

    if df_checkin.empty:
        return html.Div(
            [
                html.H3("Pulso de Bem-Estar"),
                html.Div("Ainda não há check-ins registrados."),
            ]
        )

    df_checkin_sorted = df_checkin.sort_values("dt")

    fig = px.line(
        df_checkin_sorted,
        x="dt",
        y=["stress", "stress_score"],
        markers=True,
        labels={
            "value": "Valor",
            "dt": "Data",
            "variable": "Indicador",
        },
        title="Evolução do stress (autoavaliação x score do modelo)",
    )
    return html.Div(
        [
            html.H3("Pulso de Bem-Estar"),
            dash_table.DataTable(
                columns=[{"name": col, "id": col} for col in df_checkin.columns],
                data=df_checkin.to_dict("records"),
                page_size=10,
                style_table={"overflowX": "auto"},
            ),
            dcc.Graph(figure=fig),
        ]
    )


def operacoes_layout():
    sample = pd.DataFrame(
        {
            "colaborador": ["Ana", "Bruno", "Carla", "Diego"],
            "tarefas_hoje": [5, 8, 3, 10],
            "horas_estimada": [4, 6, 2, 7],
        }
    )

    fig = px.bar(
        sample,
        x="colaborador",
        y="tarefas_hoje",
        title="Tarefas por colaborador (dados simulados)",
        labels={"tarefas_hoje": "Tarefas hoje", "colaborador": "Colaborador"},
    )

    return html.Div(
        [
            html.H3("Automação de Tarefas e Carga de Trabalho"),
            html.P("Exemplo de visão de tarefas por colaborador (dados simulados)."),
            dcc.Graph(figure=fig),
        ]
    )


def sustentabilidade_layout():
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
    conn.close()

    if df_energy.empty:
        return html.Div(
            [
                html.H3("Consumo de Energia (kWh)"),
                html.Div("Sem leituras de energia."),
            ]
        )

    df_energy_sorted = df_energy.sort_values("dt")
    fig = px.line(
        df_energy_sorted,
        x="dt",
        y="kwh",
        title="Consumo de energia ao longo do tempo",
        labels={"kwh": "kWh", "dt": "Data"},
    )

    return html.Div(
        [
            html.H3("Consumo de Energia (kWh)"),
            dash_table.DataTable(
                columns=[{"name": col, "id": col} for col in df_energy.columns],
                data=df_energy.to_dict("records"),
                page_size=10,
                style_table={"overflowX": "auto"},
            ),
            dcc.Graph(figure=fig),
        ]
    )


def inclusao_layout():
    df_inclusao = pd.DataFrame(
        {
            "grupo": ["Grupo A", "Grupo B"],
            "taxa_aprovacao": [0.65, 0.52],
        }
    )

    fig = px.bar(
        df_inclusao,
        x="grupo",
        y="taxa_aprovacao",
        title="Indicadores de Inclusão (dados simulados)",
        labels={"taxa_aprovacao": "Taxa de aprovação", "grupo": "Grupo"},
    )

    return html.Div(
        [
            html.H3("Indicadores de Inclusão (dados simulados)"),
            html.P(
                "Nesta aba, serão mostradas métricas de fairness, aprovação por grupo, etc."
            ),
            dcc.Graph(figure=fig),
            html.Small("Exemplo de diferença de taxa de aprovação entre grupos."),
        ]
    )


# ================== CALLBACKS DO CHAT ==================
@app.callback(
    Output("chat-history", "data"),
    Output("chat-input", "value"),
    Input("send-button", "n_clicks"),
    Input("chat-input", "n_submit"),
    State("chat-input", "value"),
    State("chat-history", "data"),
    prevent_initial_call=True,
)
def update_chat(n_clicks, n_submit, user_msg, history):
    if not user_msg or not user_msg.strip():
        raise PreventUpdate

    if history is None:
        history = []

    user_msg_clean = user_msg.strip()
    history.append({"role": "user", "message": user_msg_clean})

    # Se usuário digitou "sair": só envia mensagem de saída
    if user_msg_clean.lower() == "sair":
        history.append(
            {
                "role": "assistant",
                "message": "Até logo! Se precisar, é só clicar no robôzinho 🤖.",
            }
        )
        return history, ""

    # Envia mensagem ao bot
    bot_reply = route_message("dashboard_user", user_msg_clean)
    history.append({"role": "assistant", "message": bot_reply})

    return history, ""


@app.callback(
    Output("chat-messages", "children"),
    Input("chat-history", "data"),
)
def render_chat(history):
    if not history:
        return html.Div("Envie uma mensagem para começar o chat.")

    bubbles = []
    for msg in history:
        is_user = msg["role"] == "user"
        bg = "#d1e7dd" if is_user else "#f1f1f1"
        align = "flex-end" if is_user else "flex-start"

        bubbles.append(
            html.Div(
                msg["message"],
                style={
                    "maxWidth": "75%",
                    "margin": "4px 0",
                    "padding": "8px 12px",
                    "borderRadius": "8px",
                    "backgroundColor": bg,
                    "alignSelf": align,
                    "whiteSpace": "pre-wrap",
                },
            )
        )

    return html.Div(
        bubbles,
        style={"display": "flex", "flexDirection": "column"},
    )


# ================== ABRE/FECHA CHAT ==================
@app.callback(
    Output("chat-open", "data"),
    Input("open-chat-btn", "n_clicks"),
    Input("chat-history", "data"),
    State("chat-open", "data"),
    prevent_initial_call=True,
)
def toggle_chat(n_clicks, history, is_open):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "open-chat-btn":
        return not bool(is_open)

    if history:
        for msg in reversed(history):
            if msg.get("role") == "user":
                if msg.get("message", "").strip().lower() == "sair":
                    return False
                break

    return is_open


@app.callback(
    Output("chat-container", "style"),
    Input("chat-open", "data"),
)
def show_hide_chat(is_open):
    base_style = {
        "position": "fixed",
        "bottom": "90px",
        "right": "20px",
        "width": "420px",
        "height": "520px",
        "zIndex": 999,
        "backgroundColor": "white",
        "border": "1px solid #ccc",
        "borderRadius": "12px",
        "boxShadow": "0 4px 12px rgba(0,0,0,0.2)",
        "padding": "10px",
    }
    base_style["display"] = "block" if is_open else "none"
    return base_style


# ================== MAIN ==================
if __name__ == "__main__":
    app.run(debug=True)
