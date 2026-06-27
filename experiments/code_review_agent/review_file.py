
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from integration.clients import get_client
from experiments.code_review_agent.prompts import SYSTEM_PROMPT, build_file_review_prompt

import argparse

def safe_output_name(file_path: Path) -> str:
    name = file_path.name.replace(".", "_")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"review_{name}_{stamp}.md"

def offline_echo_report(file_path: Path, code: str) -> str:
    lines = code.splitlines()
    total_lines = len(lines)

    return f"""# Relatório de Revisão

## Resumo

Revisão offline gerada pelo provider `echo`.

O arquivo `{file_path}` possui {total_lines} linhas. Este modo valida o pipeline sem chamar API externa.

## Pontos positivos

- Pipeline local funcionando.
- Leitura do arquivo realizada com sucesso.
- Geração de relatório Markdown validada.

## Problemas encontrados

- O provider `echo` não executa análise semântica real do código.
- Use `openai`, `nvidia` ou `anthropic` para revisão técnica completa.

## Riscos

- Nenhum risco técnico real foi avaliado neste modo offline.
- Este resultado deve ser usado apenas como smoke test.

## Sugestões objetivas

- Rodar novamente com provider real.
- Adicionar testes automatizados para o módulo.
- Evoluir este agente para revisar diffs e PRs.

## Veredito

aprovado com ajustes
"""

def review_file(provider: str, file_path: Path, output_dir: Path, max_chars: int) -> Path:
    if not file_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"O caminho informado não é arquivo: {file_path}")

    code = file_path.read_text(encoding="utf-8", errors="replace")
    if len(code) > max_chars:
        code = code[:max_chars] + "\n\n...[conteúdo truncado para revisão]..."

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / safe_output_name(file_path)

    if provider.lower() == "echo":
        report = offline_echo_report(file_path, code)
    else:
        client = get_client(provider)
        prompt = build_file_review_prompt(str(file_path), code)
        report = client.complete(
            prompt,
            system=SYSTEM_PROMPT,
            max_tokens=700 if provider.lower() == "nvidia" else 1400,
        )

    output_path.write_text(report, encoding="utf-8")
    return output_path

def main() -> None:
    parser = argparse.ArgumentParser(description="Code Review Agent para arquivo local.")
    parser.add_argument("--provider", default="echo", help="echo, anthropic, nvidia ou openai")
    parser.add_argument("--file", required=True, help="Arquivo a ser revisado")
    parser.add_argument("--output-dir", default="experiments/code_review_agent/output", help="Diretório de saída dos relatórios")
    parser.add_argument("--max-chars", type=int, default=12000, help="Máximo de caracteres enviados ao LLM")

    args = parser.parse_args()

    output_path = review_file(
        provider=args.provider,
        file_path=Path(args.file),
        output_dir=Path(args.output_dir),
        max_chars=args.max_chars
    )
    print("== Code Review Agent ==")
    print(f"Arquivo: {args.file} ")
    print(f"Provider: {args.provider} ")
    print(f"Relatório salvo em: {output_path} ")

if __name__ == "__main__":
    main()
