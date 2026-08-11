#!/usr/bin/env python3
"""Resume um CSV coluna a coluna e grava o resultado em JSON.

Passo determinístico da skill summarize-csv: contagem, detecção de tipo,
estatísticas numéricas e valores mais frequentes. O julgamento sobre o que
esses números significam fica com o agente, não com este script.

Uso:
    python summarize_csv.py --input dados.csv
    python summarize_csv.py --input dados.csv --output resumo.json --delimiter ";"

Só usa a biblioteca padrão: a skill precisa rodar em qualquer ambiente.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_MAX_VALUES = 5
MISSING = {"", "na", "n/a", "null", "none", "-"}


def is_missing(value: str) -> bool:
    """Um valor é faltante quando está vazio ou usa um marcador convencional."""
    return value.strip().lower() in MISSING


def parse_number(value: str) -> float | None:
    """Converte texto em número aceitando vírgula decimal e separador de milhar."""
    candidate = value.strip().replace(" ", "")
    if not candidate:
        return None
    if "," in candidate and "." in candidate:
        candidate = candidate.replace(".", "").replace(",", ".")
    elif "," in candidate:
        candidate = candidate.replace(",", ".")
    try:
        number = float(candidate)
    except ValueError:
        return None
    return number


def summarize_column(name: str, values: list[str], max_values: int) -> dict[str, Any]:
    """Monta o resumo de uma coluna: contagens, tipo, estatísticas e frequências."""
    filled = [value for value in values if not is_missing(value)]
    numbers = [parse_number(value) for value in filled]
    numeric = [number for number in numbers if number is not None]
    is_numeric = bool(filled) and len(numeric) == len(filled)

    summary: dict[str, Any] = {
        "name": name,
        "count": len(values),
        "filled": len(filled),
        "missing": len(values) - len(filled),
        "unique": len(set(filled)),
        "type": "numeric" if is_numeric else "text",
        "top_values": [
            {"value": value, "count": count}
            for value, count in Counter(filled).most_common(max_values)
        ],
    }
    if is_numeric:
        summary["statistics"] = {
            "min": min(numeric),
            "max": max(numeric),
            "mean": statistics.fmean(numeric),
            "median": statistics.median(numeric),
        }
    return summary


def summarize_csv(
    path: Path, delimiter: str = ",", max_values: int = DEFAULT_MAX_VALUES
) -> dict[str, Any]:
    """Lê o CSV e devolve o resumo completo do arquivo."""
    if max_values < 1:
        raise ValueError("--max-values precisa ser maior que zero.")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle, delimiter=delimiter)
        try:
            header = next(reader)
        except StopIteration:
            raise ValueError(f"O arquivo {path.name} está vazio: não há cabeçalho.") from None
        rows = [row for row in reader if any(cell.strip() for cell in row)]

    if not header or all(not column.strip() for column in header):
        raise ValueError(f"O arquivo {path.name} não tem nomes de coluna no cabeçalho.")

    columns = [column.strip() or f"coluna_{index + 1}" for index, column in enumerate(header)]
    ragged = sum(1 for row in rows if len(row) != len(columns))
    values: dict[str, list[str]] = {column: [] for column in columns}
    for row in rows:
        for index, column in enumerate(columns):
            values[column].append(row[index] if index < len(row) else "")

    return {
        "file": path.name,
        "delimiter": delimiter,
        "rows": len(rows),
        "columns": len(columns),
        "ragged_rows": ragged,
        "column_summaries": [
            summarize_column(column, values[column], max_values) for column in columns
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Resume um arquivo CSV coluna a coluna.")
    parser.add_argument("--input", required=True, type=Path, help="Caminho do CSV de entrada.")
    parser.add_argument("--output", type=Path, help="Arquivo JSON de saída (padrão: stdout).")
    parser.add_argument("--delimiter", default=",", help='Delimitador do CSV (padrão: ",").')
    parser.add_argument(
        "--max-values",
        type=int,
        default=DEFAULT_MAX_VALUES,
        help=f"Valores mais frequentes por coluna (padrão: {DEFAULT_MAX_VALUES}).",
    )
    args = parser.parse_args()

    if not args.input.is_file():
        print(f"Arquivo não encontrado: {args.input}", file=sys.stderr)
        return 1
    try:
        summary = summarize_csv(args.input, args.delimiter, args.max_values)
    except (ValueError, UnicodeDecodeError, csv.Error) as error:
        print(f"Não foi possível resumir {args.input.name}: {error}", file=sys.stderr)
        return 1

    payload = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
        print(f"Resumo gravado em {args.output}")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
