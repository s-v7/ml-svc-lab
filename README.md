# ml-svc-lab

Laboratorio pessoal de estudos de **Machine Learning** — um guarda-chuva para
experimentar tecnicas em varios dominios. Cada experimento e autocontido e
compartilha um nucleo de utilitarios transversais. O primeiro experimento e
previsao do tempo (series temporais); outros dominios entram como novos `experiments/`.

## Estrutura

```
ml-svc-lab/
├── common/                 # utilitarios TRANSVERSAIS (qualquer experimento)
│   ├── data.py             # I/O (CSV/Parquet)
│   ├── metrics.py          # regressao (MAE/RMSE) + classificacao (acc/F1/AUC)
│   ├── splits.py           # split TEMPORAL (sem shuffle) e split aleatorio
│   └── plots.py            # previsto×real, residuos, matriz de confusao
├── experiments/
│   └── weather/            # 1o experimento — clima (series temporais)
│       ├── ingest_openmeteo.py  # baixa historico (Open-Meteo, SEM chave)
│       ├── features.py          # features + 2 alvos (temp e chuva)
│       ├── windowing.py         # janelas deslizantes (-> sklearn e Keras)
│       └── baseline.py          # persistencia / naive sazonal / climatologia
├── tests/                  # pytest do common
├── Makefile · requirements.txt · ruff.toml · .github/workflows/ci.yml
```

## Experimento weather — alvos

A partir da serie diaria, prevemos o **dia seguinte**:
- **Temperatura media** — regressao (metrica: MAE/RMSE)
- **Choveu? (>1 mm)** — classificacao (metrica: F1/AUC; acuracia engana com classe desbalanceada)

## Como rodar

```bash
make setup            # instala dependencias
make ingest           # baixa o historico de Teresina via Open-Meteo (sem chave)
make baseline         # roda os baselines (a regua dos modelos)
make test             # pytest
make lint             # ruff
```

## Baselines (a regua que os modelos de ML precisam bater)

Todo modelo so "vale" se superar o baseline ingenuo. Em validacao com serie
sintetica, a persistencia ("amanha = hoje") ja entrega temperatura com erro
baixo, e a classificacao de chuva mostra a armadilha classica: prever "nunca
chove" tem acuracia alta mas F1 = 0. Por isso medimos F1/AUC, nao acuracia.

## Metodologia (e honestidade)

Este e um **estudo de metodo**, nao um previsor que compete com servicos oficiais
(INMET/NWP usam campos espaciais, fisica e satelites; um modelo de estacao unica
nao os supera). O valor esta no rigor: baselines, **split temporal sem vazamento**,
backtest walk-forward, e comparacao justa. A mesma disciplina se aplicara aos
proximos dominios (ex.: financeiro, onde bater o "random walk" e o desafio real).

## Roadmap

- **Fase 0** — pipeline de dados + `common/` + baselines. (entregue)
- **Fase 1** — modelos sklearn (linear, MLP) vs baselines.
- **Fase 2** — TensorFlow/Keras: janelas `tf.data`, MLP, 1D-CNN, LSTM/GRU.
- **Fase 3** — avaliacao temporal + backtest walk-forward + plots.
- **Futuro** — novos `experiments/` (outros dominios e tecnicas).

## Dados

Open-Meteo Historical Weather API (ERA5, desde 1940, sem chave). Migracao futura
para INMET BDMEP (estacoes brasileiras reais). Os CSVs nao sao versionados —
gere com `make ingest`.

## License

MIT — Silas Vasconcelos Cruz ([s-v7](https://github.com/s-v7))
