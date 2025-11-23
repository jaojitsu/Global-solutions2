# 🤖 AI SPECIFICATIONS – HUM.A.N OPS (Versão Premium Glass)

## 1. Visão Geral da Arquitetura de IA

A arquitetura de Inteligência Artificial do HUM.A.N OPS funciona como um ecossistema multiagente com agentes independentes — Hygeia, Pandora, Gaia e Sophia — cada um responsável por um domínio cognitivo. Esses agentes são coordenados pelo Orquestrador, que recebe uma intenção (vinda da Pandora NLU) ou dados numéricos (Hygeia/Gaia) e decide qual agente deve responder. O design é modular, resiliente e expansível, permitindo substituição individual de modelos e integração futura com IA generativa.

**Objetivos principais:**

- Identificar estresse humano em tempo real.
- Interpretar linguagem natural e intenção do usuário.
- Detectar anomalias energéticas vindas de sensores IoT.
- Avaliar fairness e possíveis vieses.

**Fluxo cognitivo geral:**
Entrada → Inteligência Local (Agente) → Orquestrador → Ação (Dashboard/Bot).

---

## 2. Hygeia — Stress Model (RandomForestRegressor)

Hygeia é o agente de bem-estar e saúde mental. Ele transforma três respostas de check-in — motivação, cansaço e estresse — em um score contínuo entre 0 e 1 usando um modelo RandomForestRegressor.

**Inputs:** motivação (0–10), cansaço (0–10), estresse (0–10)

**Modelo:** `RandomForestRegressor(n_estimators=200)`

**Saída:** `stress_score ∈ [0, 1]`

**Classificação:**

- ≥ 0.70 → crítico
- 0.40–0.69 → moderado
- < 0.40 → baixo

**Pipeline da Hygeia:** motivação/cansaço/estresse → modelo RF → score → salvar no DB → dashboard Pessoas.

**Explainability:** Roadmap com SHAP Values para interpretar impacto de cada variável.

**Integração:** recebe dados do chatbot e do dashboard, grava no banco e alimenta visualizações.

---

## 3. Pandora – NLU + RNN Tokenizer

Pandora é o módulo de linguagem natural do HUM.A.N OPS, responsável por interpretar texto e transformá-lo em intenções estruturadas. Ela opera com um pipeline real composto por: Tokenizer → Embeddings → LSTM → Softmax.

### 3.1 Objetivo

Converter linguagem humana em intenções claras para o Orquestrador.

### 3.2 Pipeline Interno

Texto → Tokenizer → Padding → Embedding → LSTM → Dense → Softmax → Intenção.

### 3.3 Componentes

- Tokenizer converte palavras em IDs numéricos.
- Embeddings representam semântica.
- LSTM captura dependências temporais.
- Softmax seleciona a intenção mais provável.

### 3.4 Treinamento

- 40 épocas, Adam, Crossentropy.
- Dados: intents.json.

### 3.5 Exemplo

```
seq = tokenizer.texts_to_sequences(["quero fazer check-in"])
pad = pad_sequences(seq, maxlen=20)
pred = model.predict(pad)
```

### 3.6 Limitações

- Sem memória longa.
- Não lida com ironia.
- Não gera texto.

### 3.7 Evolução

- DistilBERT.
- Memória conversacional.
- Integração com Pandora Generativa.

---

## 4. Pandora Generativa – Encoder-Decoder

Pandora Generativa representa a evolução natural da Pandora NLU. Enquanto a Pandora original classifica intenções, a Pandora Generativa é uma IA **capaz de gerar linguagem**, criar explicações, microlições e respostas contextualizadas. Ela está parcialmente implementada no arquivo `pandora_generativa.py` e seguirá arquitetura **Encoder–Decoder**.

### 4.1 Objetivo

- Gerar respostas naturais e contextualizadas.
- Criar microlições e conteúdos explicativos.
- Resumir dados energéticos e de bem-estar.
- Atuar futuramente como copiloto emocional.

### 4.2 Arquitetura Base (Encoder–Decoder)

```text
Input Tokens → Embedding Layer → Encoder (LSTM/GRU)
                         → Vetor Latente → Decoder → Geração de Tokens
```

### 4.3 Funcionamento

O Encoder lê a frase e gera um vetor latente.
O Decoder usa esse vetor para prever a próxima palavra repetidamente até gerar `<EOS>`.

### 4.4 Matemática Simplificada

Encoder:
\[
h = Encoder(x*1, x_2, ..., x_n)
\]
Decoder:
\[
y_t = Decoder(y*{t-1}, h)
\]

### 4.5 Aplicações Reais Futuras

- Explicação de estresse baseada em tendência.
- Sugestões personalizadas de bem-estar.
- Geração automática de relatórios.
- Alertas inteligentes de energia.
- Microlições para onboarding corporativo.

### 4.6 Recursos Avançados (Roadmap)

- Mecanismo de Atenção (Bahdanau Attention).
- Beam Search para respostas mais naturais.
- Fine-tuning com conversas reais.
- Memória conversacional.
- Personalização por usuário.

### 4.7 Exemplo de Respostas Futuras

- "Seu estresse aumentou 12% desde terça; recomendo uma pausa de 5 minutos."
- "Gaia detectou um pico no setor B às 22h. Talvez haja equipamento ligado fora do horário."

### 4.8 Por que não está completa no MVP?

- Necessidade de dataset maior.
- Treino caro (GPU).
- Ajuste fino complexo.

### 4.9 Integração com Orquestrador

Atualmente:

```
Pandora NLU → Orquestrador → Agentes
```

Futuro:

````
Pandora Generativa → Resposta autônoma completa
```## 5. Hygeia – RandomForest Stress Engine
...

## 6. Gaia – Isolation Forest Energy Anomaly Engine
...

## 7. Sophia – Fairness Engine
...

## 8. Explainability – SHAP, Attention, Path Isolation
...

## 9. Data Pipeline
...

## 10. MLOps – Versionamento, Retraining, Drift
...

## 11. Segurança e Auditoria (LGPD + RBAC)
...

## 12. Roadmap IA Generativa Completo
...
````

## 5. Gaia – Isolation Forest Energy Anomaly Engine

Gaia é o agente responsável por analisar dados de energia provenientes do ESP32 e identificar padrões anômalos que indiquem desperdício, mau funcionamento de equipamentos ou riscos operacionais. Sua função central é detectar desvios de comportamento energético utilizando o algoritmo **Isolation Forest**, altamente eficiente para detectar outliers em séries numéricas.

### 5.1 Objetivo do Modelo

- Identificar consumos fora do padrão.
- Detectar picos de energia anormais.
- Identificar equipamentos ligados fora do horário.
- Sinalizar comportamentos atípicos em cargas elétricas.

### 5.2 Pipeline de Aquisição de Dados

```
ESP32 (SCT-013 / Sensor de Corrente)
→ Leitura ADC
→ Cálculo de corrente RMS
→ Conversão para kWh
→ API / Banco de Dados
→ Gaia realiza inferência
```

### 5.3 Modelo Isolation Forest

Utilizado devido à sua robustez contra outliers e comportamento irregular.

```
from sklearn.ensemble import IsolationForest
model = IsolationForest(n_estimators=200, contamination=0.05)
```

**Contamination = 5%** significa que o modelo assume que 5% das leituras serão anômalas.

### 5.4 Funcionamento

Gaia recebe janelas de kWh e classifica cada leitura como:

- **1 → normal**
- **-1 → anômalo**

### 5.5 Métrica Interna – Isolation Score

O modelo calcula o "path length" médio da árvore para identificar anomalias.
Valores:

- Próximos de **0** → normal
- Negativos → anomalia forte

### 5.6 Exemplos de Anomalias Detectáveis

- Pico súbito de corrente.
- Queda brusca e inesperada.
- Equipamento ligado durante a madrugada.
- Oscilações rápidas indicando mau contato.

### 5.7 Integração com o Dashboard

- **Aba Sustentabilidade:** gráfico de kWh.
- Anomalias destacadas em vermelho.
- Histórico salvo na tabela `energia`.

### 5.8 Roadmap Gaia v2

- Autoencoder para detecção mais fina.
- Cruzamento com dados climáticos.
- Previsão de consumo (LSTM).

---

## 6. Sophia – Fairness Engine

Sophia é o agente responsável por avaliar a equidade em processos internos, como aprovações, promoções e avaliações. Ela implementa métricas clássicas de fairness utilizadas em auditorias de sistemas reais.

### 6.1 Objetivo

Avaliar se grupos distintos (A, B, C…) estão sendo tratados de forma justa em processos internos.

### 6.2 Métricas Implementadas

A partir do arquivo `fairness_metrics.py`, Sophia implementa:

#### **Selection Rate (SR)**

\[ SR = rac{Aprovados}{Total\ do\ Grupo} \]

#### **Approval Gap**

\[ Gap = SR_1 - SR_2 \]
Indica diferença absoluta entre grupos.

#### **Disparate Impact (DI)**

\[ DI = rac{SR*{grupo1}}{SR*{grupo2}} \]

Regra dos 80%:

- **DI < 0.8** → possível viés
- **DI ≈ 1.0** → equidade alta

### 6.3 Como Sophia Opera

```
Entrada: tabela com colunas [grupo, aprovado]
→ Agrupamento por grupo
→ Cálculo de SR, DI e GAP
→ Retorno ao dashboard
```

### 6.4 Integração com o Dashboard

- Aba “Inclusão” exibe barras de aprovação entre grupos.
- Diferenças significativas são sinalizadas.
- Permite ao RH identificar potenciais injustiças.

### 6.5 Exemplo de Output

```
Grupo A → SR = 0.65
Grupo B → SR = 0.52
DI = 0.80 (limite mínimo)
Gap = 0.13
```

### 6.6 Roadmap Sophia v2

- Métrica de Equal Opportunity.
- Métrica de Predictive Parity.
- Relatório automático para RH.
- Auditoria contínua.

---

## 7. Explainability – SHAP, Isolation Path, Attention

Explainability é um eixo crítico dentro do HUM.A.N OPS, garantindo que todos os modelos utilizados possam ser compreendidos, auditados e analisados por humanos.

### 7.1 SHAP (Shapley Additive Explanations)

SHAP explica o impacto de cada feature em predições individuais.

### 7.2 Isolation Path – Gaia

O Isolation Forest identifica anomalias medindo o path length necessário para isolar um ponto.

### 7.3 Attention – Pandora Generativa

Permite identificar as palavras mais relevantes da entrada.

---

## 8. Data Pipeline – Fluxo Completo de Dados

O pipeline organiza a jornada de dados desde entrada até visualização.

### 8.1 Visão Geral

Entrada → Validação → Transformação → Inferência → Persistência → Dashboard

### 8.2 Validação & Transformação

- Padronização
- Normalização
- Padding de sequências

### 8.3 Inferência

Cada agente recebe dados convertidos e normalizados.

### 8.4 Persistência

Tabelas: checkin, energia, fairness, intencoes.

### 8.5 Dashboard

Dados energéticos, humanos e de fairness são exibidos em tempo real.

---

## 9. Pipeline MLOps de Ponta a Ponta

O HUM.A.N OPS adota um pipeline MLOps híbrido (manual + automatizado) que permite evolução constante dos modelos Hygeia, Pandora e Gaia, garantindo **reprodutibilidade**, **segurança**, **auditoria** e **eficiência operacional**.

### 🔄 Fluxo Geral do MLOps

1. **Coleta de Dados**

   - Check-ins → Hygeia
   - Comandos → Pandora NLU
   - Energia → Gaia

2. **Validação Inicial (Data Contracts)**

   - Tipos
   - Faixas esperadas
   - Ausência de valores nulos críticos

3. **Feature Store (Roadmap)**

   - Persistência padronizada de features para reuso entre modelos.

4. **Treinamento Automatizado (Agendado)**

   - Hygeia: semanal
   - Pandora: quinzenal
   - Gaia: diário (sensores)

5. **Versionamento de Modelos (MLflow-like)**

   - Modelo
   - Métricas
   - Dependências
   - Assinatura (input/output schema)

6. **Validação pós-treino**

   - Performance
   - Drift
   - Fairness

7. **Deploy Controlado**

   - Blue/Green
   - A/B (40/60)
   - Canary para Gaia

8. **Monitoramento Contínuo**

   - Latência
   - Acurácia
   - Mudança de distribuição

9. **Feedback Loop**
   - Uso real
   - Correções automáticas via Hygeia Learning Cycle

---

## 10. Versionamento e Gestão do Ciclo de Vida dos Modelos

Cada agente cognitivo (Hygeia, Pandora, Gaia e Sophia) possui um ciclo de vida independente, porém padronizado.

### 🏷️ Padrão de Versionamento (SemVer para ML)

```
vMAJOR.MINOR.PATCH-ML
```

- **MAJOR** → troca de arquitetura (RF → XGBoost / RNN → Encoder-Decoder)
- **MINOR** → novos dados, mesmos hiperparâmetros
- **PATCH** → ajuste fino, thresholds
- **ML** → tag indicando finalidade (stress, intent, anomaly)

**Exemplo:** `v3.2.1-stress`

### 📦 Conteúdo salvo a cada versão

- Código do modelo
- Pesos binários
- Feature importance (RF/SHAP)
- Tokenizer/word index (Pandora)
- Dataset de treino (hash verificado)
- Métricas
- Metadados (autor, data, hiperparâmetros)

### 📁 Estrutura de Diretório (Roadmap para /models)

```
models/
  hygeia/
    v3.2.1/
    v3.3.0/
  pandora_intent/
    v2.0.0/
  pandora_generativa/
    v1.0.0/
  gaia/
    v1.5.2/
```

---

## 11. Drift Detection (Data, Concept e Behavioral Drift)

O HUM.A.N OPS possui detecção tripla de drift, garantindo que os modelos se mantenham úteis mesmo em ambientes dinâmicos.

### 📊 Tipos de Drift Monitorados

#### **1) Data Drift — Mudança na distribuição das features**

Exemplos:

- Colaboradores respondendo mais 0/10 por fadiga
- Nova política de home office alterando padrões
- Mudança sazonal no uso de energia (Gaia)

Técnicas:

- KS Test
- PSI (Population Stability Index)
- Histogram Drift
- Quantile Drift

#### **2) Concept Drift — Relação entre X → y muda**

Exemplos:

- Antes, cansaço = indicativo forte de estresse
- Agora, estresse vem do time/gestão → padrão diferente

Técnicas:

- DDM (Drift Detection Method)
- EDDM (Early DDM)
- Page-Hinkley

#### **3) Behavioral Drift — Mudança no uso real**

Exemplos:

- Usuários interagem mais com bot
- Frases novas não vistas no tokenizer

Pandora é sensível a isso e aciona um retraining.

---

## 12. Retraining Automático (Híbrido)

Cada agente possui sua própria estratégia de retraining.

### 🤖 Hygeia (RandomForestRegressor)

- Retraining semanal
- Janelas deslizantes de 30 dias
- Validação automática
- Thresholds atualizados dinamicamente

### 🧠 Pandora NLU (RNN + Tokenizer)

- Retraining quinzenal
- Novas frases do bot são adicionadas
- Tokenizer é expandido
- OOV (Out-of-Vocabulary) monitorado

### ⚡ Gaia (Isolation Forest)

- Retraining diário
- Sensível a temperatura, carga e horários
- Deploy Canary: 10% dos dados testam o novo modelo

### ⚖️ Sophia (Fairness Engine)

- Retraining mensal
- Novas métricas demográficas
- Normalização estadística

---

## 13. Monitoramento em Produção (Observabilidade de IA)

### 📍 Métricas coletadas continuamente

| Componente  | Métricas                                              | Tipo                |
| ----------- | ----------------------------------------------------- | ------------------- |
| Hygeia      | MSE, MAE, resposta média, frequência de check-in      | Qualidade/uso       |
| Pandora NLU | Intents corretas, OOV %, latência, perplexidade       | Qualidade/Linguagem |
| Gaia        | Score médio, número de anomalias, picos, latência IoT | Operacional         |
| Sophia      | Drifts, fairness gap, distribuições                   | Ética               |

### 🔎 Painel de Observabilidade (Roadmap)

- Grafana
- Prometheus
- Painéis por agente
- Alertas em Teams quando drift > threshold

---

## 14. Processo de Aprovação (Human-in-the-Loop)

Para modelos que afetam saúde mental, fairness ou registros críticos:

1. Treinamento automático
2. Validação automática
3. Validação humana obrigatória
4. Deploy controlado
5. Auditoria registrada

Aplicado a:

- Hygeia
- Sophia
- Pandora Generativa

---

## 15. Governança de Modelos (AI Governance Layer)

### Componentes principais

- Catálogo de modelos
- Policy engine
- Checklists de conformidade
- Auditoria legal (LGPD)
- Histórico de performance

### Controles

- Quem pode aprovar
- Quem pode treinar
- Quem pode apagar versão
- Quem acessa logs sensíveis

---

## 16. Segurança e Auditoria (LGPD + RBAC)

### 🔐 Visão Geral

A camada de segurança do HUM.A.N OPS foi projetada com foco em **privacidade**, **controle de acesso** e **auditoria contínua**, garantindo conformidade com a **LGPD** e com práticas modernas de Zero Trust.

---

### 🛡️ 16.1. LGPD – Mecanismos Implementados

**Coleta Minimizada (Data Minimization):**

- Somente dados essenciais são coletados (check-ins, energia, interações do bot).
- Nenhum dado sensível é armazenado sem consentimento explícito.

**Pseudonimização:**

- Cada colaborador recebe um `worker_hash_id` irreversível.
- Dashboards de RH só acessam dados agregados.
- Modelos nunca veem nomes reais.

**Direito ao Esquecimento:**

- Rotina `delete_worker_records(worker_id)` remove todas as ocorrências em 4 bancos:
  - PostgreSQL (relacional)
  - TimescaleDB (séries temporais)
  - JSON logs dos bots
  - Arquivos de relatório

**Transparência:**

- Logs de auditabilidade registram:
  - quem acessou,
  - quando acessou,
  - qual módulo,
  - e qual justificativa.

---

### 🔒 16.2. Zero Trust Architecture

**Princípios:**

1. Nunca confiar — sempre verificar.
2. Acesso mínimo necessário.
3. Autenticação contínua.

**Implantações no sistema:**

- Tokens OAuth2 com expiração curta.
- Revalidação a cada operação crítica.
- Chaves rotacionadas automaticamente.
- Assinatura de payloads enviados pelo IoT Gateway.

---

### 👤 16.3. RBAC – Role-Based Access Control

**Perfis disponíveis:**
| Perfil | Permissões |
|--------|------------|
| Colaborador | Registrar check-ins, consultar microlições |
| Gestor | Acessar dashboards agregados, ver risco da equipe |
| RH | Acessar histórico individual com consentimento |
| Operações | Acessar módulos de energia e estoque |
| Admin | CRUD completo dos módulos + auditoria |

**Fluxo:**

```
Requisição → Middleware RBAC → Verificação de Claim → Acesso ou Bloqueio → Log de Auditoria
```

---

### 📜 16.4. Auditoria em Quatro Camadas

**1) Auditoria de Acesso**

- Toda rota protegida gera um evento `access_log` em PostgreSQL.

**2) Auditoria de Alteração**

- Atualizações de energia, estoque e check-in geram snapshots.

**3) Auditoria de ML**

- Cada predição do modelo gera:
  - valor predito,
  - dados de entrada,
  - versão do modelo.

**4) Auditoria Conversacional**

- A Pandora registra intenções classificadas (NLU Logs).

---

## 16. Roadmap IA Generativa Completo

### 🧠 Objetivo

Evoluir o HUM.A.N OPS de IA Clássica (RF, IsolationForest, RNN simples) para uma arquitetura híbrida **Generativa + Multiagente** com capacidade de:

- gerar recomendações personalizadas,
- criar planos de bem-estar adaptativos,
- explicar decisões em linguagem natural,
- atuar de forma autônoma.

---

### 🚀 Fase 1 — Expansão Generativa (1–2 meses)

**Pandora Generativa:**

- Migrar para encoder-decoder.
- Geração de respostas empáticas.
- Fine-tuning com dataset interno de comandos reais.

**Saídas esperadas:**

- /checkin mais conversacional.
- Feedback personalizado.

---

### 🚀 Fase 2 — Multiagente Generativo (3–5 meses)

**Agentes previstos:**

- Pandora-Linguagem (LLM pequeno)
- Hygeia-Coach (bem-estar)
- Gaia-Optimizer (energia & CO₂)
- Sophia-Fairness Advisor

**Feature-chave:**

- “Mini reuniões internas” entre agentes antes de responder ao usuário.

---

### 🚀 Fase 3 — Ações Autônomas (5–9 meses)

- O sistema começa a tomar decisões automáticas, por exemplo:
  - sugerir revezamentos de carga,
  - bloquear tarefas excessivas,
  - propor reorganização de horários.

**Tecnologias:**

- LangChain Agents
- LangGraph workflows
- Policy RL (Reinforcement Learning)

---

### 🚀 Fase 4 — Digital Twin Humano (9–18 meses)

Criação de um “espelho digital” de cada colaborador com:

- baseline energético,
- baseline emocional,
- baseline cognitivo,
- histórico longitudinal.

Isso permite predições de:

- burnout em 7–14 dias,
- quedas de produtividade,
- risco de abandono.

---

### 🚀 Fase 5 — Plataforma Autônoma (2 anos)

O HUM.A.N OPS se torna uma plataforma vivo-adaptativa:

- Modelos se atualizam sozinhos (MLOps completo)
- Regras geradas automaticamente
- Recomendações 100% personalizadas

**Resultado esperado:**
A empresa opera com um copiloto cognitivo real, não apenas analítico.

---
