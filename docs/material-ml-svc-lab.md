# ML Service Lab — Roadmap de Vitrine Técnica

## Objetivo

Construir um laboratório prático de ML, LLM, vetores, RAG, avaliação e integração corporativa, demonstrando uso aplicado de IA em cenários reais de software, documentação, código legado, segurança e análise de dados.

O projeto deve servir como vitrine técnica para oportunidades em IA aplicada, backend, sistemas corporativos, revisão de código, automação institucional e freelancing técnico.

---

## Stack base

* Python 3.12
* OpenAI SDK
* NVIDIA NIM
* Anthropic SDK
* FAISS ou pgvector
* scikit-learn
* pandas
* pytest
* ruff
* GitHub/Git
* Integração futura com Java/Spring/legado corporativo

---

## Módulos planejados

### 001 — Vector RAG

Implementar busca semântica com embeddings.

Objetivo:

* Ler documentos locais
* Quebrar em chunks
* Gerar embeddings
* Armazenar vetores
* Recuperar contexto por similaridade
* Responder perguntas com base nos documentos

Entregáveis:

* `integration/embeddings.py`
* `experiments/rag/ingest_docs.py`
* `experiments/rag/ask_docs.py`
* Base vetorial local
* Teste com README e documentação do projeto

---

### 002 — Reranking

Adicionar reranking para melhorar a qualidade do RAG.

Objetivo:

* Recuperar top_k documentos por vetor
* Reordenar candidatos por relevância
* Comparar RAG com e sem reranking

Entregáveis:

* `integration/reranker.py`
* `experiments/rag/eval_rag.py`
* Métrica simples de precisão manual
* Comparativo de resultados

---

### 003 — Code RAG

Criar RAG sobre código-fonte.

Objetivo:

* Indexar arquivos `.py`, `.java`, `.ts`, `.js`, `.xhtml`, `.md`
* Permitir perguntas técnicas sobre o código
* Explicar módulos, funções e responsabilidades
* Apoiar análise de legado e onboarding técnico

Entregáveis:

* `experiments/code_rag/index_code.py`
* `experiments/code_rag/ask_code.py`
* Filtro por extensão
* Resposta com arquivo de origem

---

### 004 — Document Intelligence

Criar pipeline para análise de PDFs, tabelas e gráficos.

Objetivo:

* Ler documentos institucionais
* Extrair texto, tabelas e estruturas
* Gerar resumo técnico
* Preparar conteúdo para RAG

Entregáveis:

* `experiments/document_ai/extract_pdf.py`
* `experiments/document_ai/extract_tables.py`
* `experiments/document_ai/summarize_document.py`

---

### 005 — Code Review Agent

Criar agente de revisão de código com LLM.

Objetivo:

* Revisar arquivos alterados
* Avaliar qualidade, clareza, bugs e riscos
* Gerar relatório estruturado
* Simular revisão de PR/issue
* Aproximar o projeto de oportunidades como Vetto e freelancing técnico

Escopo inicial:

* Entrada: arquivo local ou diff `.patch`
* Saída: relatório Markdown
* Modo offline com `echo`
* Modo real com `openai`, `nvidia` ou `anthropic`

Critérios de revisão:

* Clareza dos requisitos
* Correção lógica
* Bugs prováveis
* Segurança
* Tratamento de erro
* Testabilidade
* Performance
* Manutenibilidade
* Sugestões objetivas

Entregáveis:

* `experiments/code_review_agent/review_file.py`
* `experiments/code_review_agent/review_diff.py`
* `experiments/code_review_agent/prompts.py`
* `experiments/code_review_agent/output/`
* Exemplo de relatório Markdown

Comando esperado:

```bash
PYTHONPATH=. python3 -m experiments.code_review_agent.review_file --provider echo --file integration/clients.py
```

Saída esperada:

```text
== Code Review Agent ==
Arquivo: integration/clients.py
Provider: echo
Status: relatório gerado
```

---

### 006 — LGPD / PII Detection

Criar módulo para detectar e anonimizar dados sensíveis.

Objetivo:

* Detectar CPF, e-mail, telefone, nome e identificadores
* Gerar versão anonimizada
* Criar relatório de risco LGPD

Entregáveis:

* `experiments/privacy/pii_detect.py`
* `experiments/privacy/redact_text.py`
* `experiments/privacy/audit_report.py`

---

### 007 — Weather Forecast Baseline

Manter o módulo climático como avaliação comparativa.

Objetivo:

* Comparar persistência, sklearn e LLM
* Medir MAE
* Medir latência
* Registrar quando LLM bate ou perde da baseline

Entregáveis:

* Resultado CSV
* Gráficos
* Comparativo por provider
* Conclusão técnica no README

---

## Ordem de implementação sugerida

1. Code Review Agent
2. Vector RAG
3. Code RAG
4. Reranking
5. Weather baseline com relatório
6. LGPD / PII
7. Document Intelligence

---

## Estratégia de commit

Usar padrão SV7 1:1:

* Uma issue por entrega
* Um commit por mudança coerente
* README atualizado a cada módulo
* Teste mínimo por módulo
* Modo offline sempre disponível via provider `echo`

---

## Visão final

Este laboratório deve demonstrar que LLM não é apenas chat, mas uma camada de inteligência integrada a sistemas reais:

* revisão de código
* análise de documentos
* busca semântica
* explicação de legado
* avaliação com métricas
* segurança e LGPD
* integração com backend corporativo

