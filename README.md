# ml-svc-lab

Laboratório pessoal de **Machine Learning, LLMs, busca vetorial, RAG, agentes de revisão de código e avaliação técnica**.

O projeto começou como um experimento de previsão climática com séries temporais, baselines e modelos clássicos de ML. Agora evolui para uma vitrine de IA aplicada a cenários reais de engenharia de software, documentação, código legado, avaliação com métricas e integração corporativa com ecossistemas Python, Java e NodeJs.
## Objetivo

Demonstrar, de forma prática e versionada, como combinar:

* Machine Learning clássico
* LLMs via OpenAI, NVIDIA NIM e Anthropic
* Busca vetorial e embeddings
* RAG com reranking
* Agentes de revisão de código
* Avaliação com métricas e baselines
* Document Intelligence
* LGPD / PII detection
* Integração futura com sistemas corporativos Javax/Jakarta EE/Spring

A premissa do laboratório é simples:

> LLM não deve ser tratado como mágica. Cada módulo precisa ter entrada clara, saída verificável, baseline, avaliação e modo offline para testes.

---

## Módulos

```text
ml-svc-lab/
├── common/                     # utilitários transversais
│   ├── data.py                 # I/O de dados
│   ├── metrics.py              # métricas de regressão/classificação
│   ├── splits.py               # splits temporais e aleatórios
│   └── plots.py                # gráficos e diagnóstico visual
├── integration/                # clients e integração com LLMs
│   ├── clients.py              # interface única: openai, nvidia, anthropic, echo
│   ├── narrator.py             # LLM como narrador de resultados
│   └── README.md
├── experiments/
│   ├── weather/                # baseline climático: ML clássico vs LLM
│   └── code_review_agent/      # agente de revisão de código com LLM
├── docs/
│   ├── material-ml-svc-lab.md  # roadmap geral da vitrine
│   └── issues/                 # issues locais por módulo
├── tests/
├── Makefile
├── requirements.txt
└── ruff.toml
```

---

## Roadmap

| Issue | Módulo                |      Status      |
| ----: | --------------------- | :--------------: |
|   001 | Vector RAG            |     planejado    |
|   002 | Reranking             |     planejado    |
|   003 | Code RAG              |     planejado    |
|   004 | Document Intelligence |     planejado    |
|   005 | Code Review Agent     | em implementação |
|   006 | LGPD / PII Detection  |     planejado    |
|   007 | Weather Baseline      |     iniciado     |

---

## Code Review Agent

O módulo `experiments/code_review_agent/` implementa um agente local de revisão de código usando LLM.

Ele suporta:

* revisão de arquivo local
* providers `echo`, `openai`, `nvidia` e `anthropic`
* geração de relatório Markdown
* modo offline para smoke test
* ajuste de `max_tokens` por provider
* base para evolução futura com revisão de diff/PR

### Rodar revisão offline

```bash
PYTHONPATH=. python3 -m experiments.code_review_agent.review_file \
  --provider echo \
  --file integration/clients.py
```

### Rodar revisão com OpenAI

```bash
PYTHONPATH=. python3 -m experiments.code_review_agent.review_file \
  --provider openai \
  --file integration/clients.py
```

### Rodar revisão com NVIDIA NIM

```bash
PYTHONPATH=. python3 -m experiments.code_review_agent.review_file \
  --provider nvidia \
  --file integration/clients.py
```

Os relatórios são salvos em:

```text
experiments/code_review_agent/output/
```

Os arquivos `.md` gerados nessa pasta são artefatos locais e não devem ser versionados.

---

## Integração com LLMs

A camada `integration/clients.py` fornece uma interface única:

```python
client.complete(prompt, system="", max_tokens=None) -> str
```

Providers disponíveis:

| Provider    | SDK         | Variável de ambiente | Uso               |
| ----------- | ----------- | -------------------- | ----------------- |
| `echo`      | nenhum      | nenhuma              | testes offline    |
| `openai`    | `openai`    | `OPENAI_API_KEY`     | geração e revisão |
| `nvidia`    | `openai`    | `NVIDIA_API_KEY`     | NVIDIA NIM        |
| `anthropic` | `anthropic` | `ANTHROPIC_API_KEY`  | Claude            |

Instalação dos SDKs:

```bash
python3 -m pip install openai anthropic
```

---

## Weather Forecast Baseline

O experimento `experiments/weather/` mantém o estudo original de previsão do tempo.

Ele compara:

* persistência
* modelos sklearn
* LLM como previsor
* métricas como MAE, RMSE, F1 e AUC
* split temporal sem vazamento

### Rodar baseline sklearn

```bash
PYTHONPATH=. python3 -m experiments.weather.train_sklearn
```

### Rodar LLM forecaster offline

```bash
PYTHONPATH=. python3 -m experiments.weather.llm_forecaster \
  --provider echo \
  --n 30
```

### Rodar LLM forecaster com provider real

```bash
PYTHONPATH=. python3 -m experiments.weather.llm_forecaster \
  --provider nvidia \
  --n 3
```

Observação: LLMs podem ser lentos e instáveis em previsão numérica. O objetivo aqui é medir e comparar, não assumir que o LLM sempre vence a baseline.

---

## Baselines: a régua que os modelos precisam bater

Todo modelo só vale se superar um baseline simples. No dado real de Teresina, a persistência — “amanhã = hoje” — entrega temperatura com erro baixo. Na classificação de chuva, também aparece uma armadilha clássica: prever “nunca chove” pode ter acurácia alta, mas F1 ruim. Por isso o projeto mede F1/AUC, não apenas acurácia.

---

## Resultados — Fase 1: dado real de Teresina

Modelos clássicos com sklearn comparados aos baselines no conjunto de teste temporal.

Régua inicial:

* Temperatura: **MAE 0.637** com persistência
* Chuva: **F1 0.759** com persistência

| Alvo        | Modelo             | Métrica              | Bateu baseline? |
| ----------- | ------------------ | -------------------- | :-------------: |
| Temperatura | persistência       | MAE=0.637            |     baseline    |
| Temperatura | LinearRegression   | MAE=0.615            |       sim       |
| Temperatura | Ridge(α=1)         | MAE=0.615            |       sim       |
| Temperatura | MLPRegressor       | MAE=0.638            |       não       |
| Chuva       | persistência       | F1=0.759             |     baseline    |
| Chuva       | LogisticRegression | F1=0.750 / AUC=0.900 |    não no F1    |
| Chuva       | MLPClassifier      | F1=0.759 / AUC=0.895 |     empatou     |

Leitura técnica:

> Na temperatura, a regressão linear supera a persistência por pouco, enquanto o MLP piora. Em sinal quase determinístico, mais complexidade não necessariamente ajuda. Na chuva, a regressão logística não bate o F1, mas apresenta AUC alto, indicando que ranqueia bem o risco; falta calibrar melhor o limiar de decisão.

<div align="center">

![Temperatura: previsto vs real](experiments/weather/plots/temp_pred_vs_real.png)

![Resíduos da temperatura](experiments/weather/plots/temp_residuos.png)

![Matriz de confusão — chuva](experiments/weather/plots/chuva_confusao.png)

</div>

---

## Resultados iniciais com LLM forecaster

Resultados observados nos testes locais:

| Provider |  n | Baseline MAE | LLM MAE | Resultado            |
| -------- | -: | -----------: | ------: | -------------------- |
| echo     | 30 |        0.309 |   0.309 | igual à persistência |
| openai   | 30 |        0.309 |   0.417 | não bateu            |
| nvidia   |  1 |        0.167 |   0.331 | não bateu            |
| nvidia   |  3 |        0.275 |   0.233 | bateu                |
| nvidia   |  5 |        0.228 |   0.235 | não bateu            |

Leitura técnica:

> A persistência é uma baseline forte para séries climáticas. LLM puro não é garantia de melhoria numérica, mas pode ser útil como camada explicativa, avaliadora ou integradora.

---

## Metodologia e honestidade

Este é um estudo de método, não um previsor que compete com serviços oficiais. INMET, NWP e serviços meteorológicos usam campos espaciais, física, satélites e redes de observação. Um modelo simples de estação única não substitui isso.

O valor do projeto está no rigor:

1. Baseline antes de modelo complexo.
2. Split temporal quando o dado envolve tempo.
3. Modo offline sempre disponível.
4. LLM com saída verificável.
5. Relatório técnico em Markdown.
6. Separação entre cálculo, narração e avaliação.
7. Integração incremental com provedores reais.
8. Commits pequenos no padrão SV7 1:1.

---

## Dados

O experimento climático usa dados da Open-Meteo Historical Weather API, sem chave.

Migração futura planejada:

* INMET BDMEP
* estações brasileiras reais
* comparação por cidade/estado
* enriquecimento com variáveis meteorológicas adicionais

Os CSVs de dados brutos não precisam ser versionados. Gere com:

```bash
make ingest
```

---

## Licença

MIT — Silas Vasconcelos Cruz ([s-v7](https://github.com/s-v7))

