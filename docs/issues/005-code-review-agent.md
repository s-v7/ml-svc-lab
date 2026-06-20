# Issue 005 — Implementar Code Review Agent

## Objetivo

Criar um agente local de revisão de código usando LLM, capaz de analisar arquivos ou diffs e gerar um relatório técnico em Markdown.

## Motivação

Este módulo conecta o `ml-svc-lab` com oportunidades de revisão técnica, freelancing, avaliação de código, GitHub e projetos como Vetto.

## Escopo inicial

- Revisar um arquivo local
- Revisar um diff local futuramente
- Suportar providers: echo, openai, nvidia, anthropic
- Gerar relatório em Markdown
- Salvar saída em `experiments/code_review_agent/output/`

## Arquivos previstos

- `experiments/code_review_agent/__init__.py`
- `experiments/code_review_agent/prompts.py`
- `experiments/code_review_agent/review_file.py`
- `experiments/code_review_agent/review_diff.py`
- `experiments/code_review_agent/output/.gitkeep`

## Critérios de aceite

- [ ] Rodar com provider `echo`
- [ ] Rodar com provider real
- [ ] Aceitar `--file`
- [ ] Gerar relatório Markdown
- [ ] Não quebrar imports existentes
- [ ] Passar em `py_compile`
- [ ] Documentar uso no README

## Comando esperado

```bash
PYTHONPATH=. python3 -m experiments.code_review_agent.review_file --provider echo --file integration/clients.py
Resultado esperado
== Code Review Agent ==
Arquivo: integration/clients.py
Provider: echo
Relatório salvo em: experiments/code_review_agent/output/review_clients.md
```


