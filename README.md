# 🌱 HUM.A.N OPS – Human-Aware & Sustainable Operations

### Global Solution – Fase Final · FIAP

## 👨‍🚀 Equipe Rocket

- <a href="https://www.linkedin.com/in/jonas-silva-0a659892/">Jonas Luis da Silva</a>
- <a href="https://www.linkedin.com/in/jo%C3%A3o-vitor-severo-oliveira-87904134b/">João Vitor Severo Oliveira</a>
- <a href="https://www.linkedin.com/in/edson-henrique-felix-batista-a00191123/">Edson Henrique Felix Batista</a>
  **Tutor:** Lucas Gomes Moreira  
  **Coordenador:** André Godoi Chiovato

---

# 🎥 Vídeo da Apresentação

[![Vídeo de Apresentação](https://img.youtube.com/vi/5PL3FIZcALk/mqdefault.jpg)](https://www.youtube.com/watch?v=5PL3FIZcALk)

---

## 📁 [Repositório Oficial(Privado)](https://github.com/jonsilva91/Global-Solutions2)

---

# 🎯 Visão Geral da Solução

O **HUM.A.N OPS** é uma plataforma inteligente que integra **bem-estar, produtividade, sustentabilidade e inclusão**, criando ambientes de trabalho mais humanos e eficientes.

A solução combina:

- **IA clássica (ML)** para previsão de estresse e detecção de anomalias.
- **Agentes inteligentes** (Atena, Hygeia, Gaia e Sophia).
- **Bot copiloto** com análise de intenção (NLU).
- **Dashboard interativo** para tomada de decisões.
- **Relatórios em R** para profundidade analítica.

---

# 🤖 Os 5 Agentes Inteligentes

### **Atena – Produtividade**

Organização de tarefas, relatórios automáticos e suporte operacional.

### **Hygeia – Bem-Estar**

Check-ins de saúde mental + modelo de Regressão Logística para previsão de estresse.

### **Gaia – Sustentabilidade**

Análise energética + modelo Isolation Forest para detectar desperdícios.

### **Sophia – Inclusão e Ética**

Avaliação de fairness e identificação de possíveis desigualdades.

### **Pandora – NLU Emocional e Interpretação de Linguagem**

Responsável por interpretar mensagens abertas do usuário, detectar emoção, intenção secundária e tonalidade.

- Classificação emocional via RandomForestRegressor (alegria, tristeza, raiva, neutro)
- Pipeline RNN+Tokenizer + Regras heurísticas para intenção
- Apoia Hygeia e Atena fornecendo contexto emocional e histórico de linguagem
- Implementada em `pandora.py` e `pandora_nlu.py`

Avaliação de fairness e identificação de possíveis desigualdades.

---

# 🧠 IA Aplicada

### **Modelo 1 – Hygeia (Risco de Estresse)**

- Algoritmo: **RandomForestRegressor**
- Input: motivação, cansaço, estresse
- Output: probabilidade de risco (baixo, médio, alto)

- ![chatbot Hygeia](/assets/chat_Hygeia.png)

### **Modelo 2 – Gaia (Anomalia de Energia)**

- Algoritmo: **Isolation Forest**
- Input: consumo kWh
- Output: normal ou anômalo

### **Modelo 3 – Sophia (Fairness)**

- Métrica: **Disparate Impact**
- Objetivo: analisar possíveis vieses em dados de aprovação

### **Modelo 4 – Pandora (Saúde Mental)**

- Algoritmo: **RNN + Tokenizer**
- Input: mensagens
- Output: mensagens de incentivo ou encaminhamento a especialista

- ![chatbot Pandora](/assets/chat_pandora.png)

### **Modelo 5 – Atena (Produtividade & Suporte Operacional)**

- Algoritmo: **Regras de intenção + Recuperação estruturada (NLU leve)**
- Input: comandos do usuário (tarefas, relatorio, organizar, como fazer, checklist)
- Output: Lista de tarefas do dia, Geração de relatórios operacionais, Orientações rápidas (excel, processos, políticas internas), Ações automatizadas (simulação: montar checklist, gerar resumo semanal)

---

# 🧩 Arquitetura da Solução

Veja o arquivo completo em [Diagramas C4](./document/architecture/human_c4_diagrams.html).

Fluxo resumido:

```
Usuário → Bot Copiloto → API FastAPI → Banco SQLite(para MVP substituivel por PostgreSQL)
                                  ↓
                     Modelos de IA (Stress / Energia / Fairness)
                                  ↓
                         Dashboard (Dash / Plotly)
```

---

# 🖥️ Como Rodar a Solução

### **1. Criar ambiente virtual**

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### **2. Instalar dependências**

```bash
pip install -r config/requirements.txt
```

### **3. Inicializar o Banco + Modelos IA**

```bash
python scripts/init_db.py
```

### **4. Subir a API**

```bash
uvicorn src.api.main:app --reload
```

Acesse: http://127.0.0.1:8000/docs

### **5. Subir o Dashboard (Dash/Plotly)**

```bash
python src/dashboard/app_dash.py
```

---

# 📊 Funcionalidades do Dashboard

### **👤 Pessoas**

Check-ins, gráficos de stress/motivação/cansaço.

### **⚙️ Operações**

Carga de tarefas, produtividade (dados simulados).

### **🌍 Sustentabilidade**

Consumo energético + detecção de picos.

### **🤝 Inclusão**

Diferença de aprovação entre grupos.

---

# 📘 Integração com Disciplinas FIAP

### **Python:** API, bot, dashboard e ML.

### **Machine Learning:** RandomForestRegressor, Isolation Forest.

### **Redes Neurais:** Base conceitual usada no Pandora NLU.

### **R / Estatística:** Relatórios (human_ops_report.pdf).

### **ESP32:** Detecção de anomalias energeticas.

### **Banco de Dados:** SQLite + scripts SQL(MVP). PostgreSQL na produção

### **Cloud:** Deploy possível via Uvicorn/Docker.

### **Cybersecurity:** Princípios de privacidade, consentimento, RBAC simples.

### **Formação Social:** Impacto humano, ética, inclusão e ESG.

### **AICSS:** Futuro do trabalho humanizado + automação ética.

### **AI Challenge:** Integração mostrada no vídeo.

---

## 🚀 **GUIA RÁPIDO PARA AVALIADORES**

> **⏱️ Tempo estimado de revisão: 15–20 minutos para o essencial**
>
> Por ser um projeto completo (API + IA + Dashboard + R + Bot), recomendamos a seguinte ordem de avaliação para uma experiência rápida e objetiva.

### 📋 **Roteiro de Avaliação Recomendado**

1. **🟢 README.md (você está aqui)**

   - Entenda o propósito do HUM.A.N OPS
   - Visão geral dos 5 agentes inteligentes (Atena, Hygeia, Gaia, Sophia, Pandora)
   - Guia de execução da solução
   - Arquitetura resumida

2. **🎬 Vídeo de Demonstração** _(link no topo do README)_

   - Fluxo completo funcionando: Bot → API → IA → Dashboard
   - Detecção de estresse (Hygeia) e anomalias (Gaia)
   - Copiloto on‑line (chat integrado)

3. **🏗️ Diagramas C4 Interativos**

   - [Diagramas C4](./document/architecture/human_c4_diagrams.html)
   - Visualize a arquitetura completa em nível de Containers e Componentes
   - Clareza sobre a integração Backend + IA + Dashboard + Bot

4. **📚 Documentação Mestra**

   - [master_documentantion.md](./master_documentation.md)
   - Arquitetura detalhada, justificativas técnicas, decisões de design
   - Fluxos e casos de uso

5. **🧠 Especificações de IA**
   - [document/ai_specifications.md](./document/ai_specifications)
   - Modelos: Stress (Hygeia), Energia (Gaia), Fairness (Sophia), NLU (Pandora)
   - Dados sintéticos, features e técnicas usadas

### 🎯 **Pontos de Destaque para Focar**

- **MVP 100% funcional** (API + IA + Dashboard + Bot + R)
- **IA aplicada de forma ética** (bem‑estar, inclusão, sustentabilidade)
- **Arquitetura sólida e modular**
- **Bot copiloto com NLU (Pandora)**
- **Dashboard profissional (Dash/Plotly)**

### ⚡ **Para Revisão Expressa (10 minutos)**

Se o tempo for curto, recomendamos olhar:

1. **Dashboard funcionando** (`app_dash.py`)
2. **API funcionando** (`/checkin` e `/energia/status`)
3. **Modelos de IA** (stress e anomalia)
4. **C4 – visão macro**
5. **Relatório R (human_ops_report.pdf)**

---

# 🗂️ Estrutura do Repositório

```
Global-Solutions2/
├── assets/
├── config/
│   ├── db/
│    │    └── human_ops.db
│    └── requirements.txt
├── document/
│   └── architeture/
    │      └── human_c4_diagrams.html
│   ├── human_ops_report.pdf
│   ├── *.md (a gerar)
├── scripts/
│   └── init_db.py
├── src/
│   ├── api/
│   ├── bot/
│   ├── dashboard/
│   ├── data/
│   ├── ml/
│   └── core/
└── README.md
```

---

# 📌 Evidências Funcionais

- ✔ Check-in registrado → stress previsto por IA
- ✔ Pico de energia → anomalia detectada
- ✔ Dashboard dinâmico
- ✔ Bot copiloto ativo com interpretação de intenções
- ✔ Relatório em R gerado

---

# 📄 Licença

Projeto acadêmico – FIAP – Global Solution
