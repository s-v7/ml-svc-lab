# integration/

Camada de integração com LLMs para o `ml-svc-lab`. Dois papéis distintos:

1. **Narrador** (`narrator.py`) — recebe os resultados já calculados pelos modelos
   e gera um resumo em prosa. Princípio herdado do `grafos_municipios_br`: **os
   modelos são o oráculo; o LLM apenas descreve, nunca recalcula nem inventa.**

2. **Previsor** (`../experiments/weather/llm_forecaster.py`) — o LLM tenta prever
   a série e é avaliado com `common.metrics` contra os baselines, no mesmo split
   temporal. Honesto: LLMs são fracos em séries numéricas; o objetivo é **medir**
   isso com rigor, não vencer.

## Provedores (interface única `complete(prompt, system="") -> str`)

| provider    | SDK            | variável de ambiente | observação                         |
|-------------|----------------|----------------------|------------------------------------|
| `openai`    | `openai`       | `OPENAI_API_KEY`     | gpt-4o-mini por padrão             |
| `anthropic` | `anthropic`    | `ANTHROPIC_API_KEY`  | Claude                             |
| `nvidia`    | `openai`       | `NVIDIA_API_KEY`     | NIM, endpoint compatível c/ OpenAI |
| `echo`      | —              | —                    | offline, p/ testes (sem rede)      |

Os SDKs são importados sob demanda — importar `clients.py` não exige tê-los
instalados. Instale só o do provedor que for usar:

```bash
pip install openai       # cobre openai E nvidia (mesmo SDK)
pip install anthropic    # para o provider anthropic
```

## NVIDIA: NIM ≠ CUDA

- **NIM** (`integrate.api.nvidia.com/v1`) é um **serviço de inferência** na nuvem
  (manda prompt, recebe texto) — é o que este módulo usa, ao lado de OpenAI.
- **CUDA/cuDNN** é a stack de **GPU para acelerar treino local** do TensorFlow.
  Não é API; é infra de treino. Sem relação com `integration/`.

## Uso

```bash
# narrador (resultados -> prosa)
PYTHONPATH=. python3 -c "from integration.narrator import narra; \
  print(narra({'temp_mae': 0.615, 'baseline': 0.637}, provider='openai'))"

# previsor (LLM como baseline), offline para testar o pipeline:
PYTHONPATH=. python3 -m experiments.weather.llm_forecaster --provider echo --n 20
# real (precisa da chave):
PYTHONPATH=. python3 -m experiments.weather.llm_forecaster --provider nvidia --n 30
```
