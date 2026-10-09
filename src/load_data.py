"""Importa o CSV de leituras IoT para o PostgreSQL.

Uso: python src/load_data.py
A execução substitui o conteúdo da tabela pelos registros do CSV atual,
mas preserva todas as linhas de origem, inclusive IDs repetidos.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def get_engine() -> Engine:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL não definida. Copie .env.example para .env e configure a senha do PostgreSQL."
        )
    return create_engine(database_url, pool_pre_ping=True)


def main() -> int:
    csv_value = os.getenv("CSV_PATH", "data/IOT-temp.csv")
    csv_path = Path(csv_value)
    if not csv_path.is_absolute():
        csv_path = ROOT / csv_path
    if not csv_path.exists():
        raise FileNotFoundError(
            f"CSV não encontrado: {csv_path}\nColoque IOT-temp.csv na pasta data/ do projeto."
        )

    print(f"Lendo arquivo: {csv_path}")
    raw = pd.read_csv(csv_path, encoding="utf-8-sig", low_memory=False)
    raw.columns = raw.columns.str.strip()
    expected = {"id", "room_id/id", "noted_date", "temp", "out/in"}
    missing = expected - set(raw.columns)
    if missing:
        raise ValueError(
            f"O CSV não contém as colunas esperadas: {sorted(missing)}. "
            f"Colunas encontradas: {raw.columns.tolist()}"
        )

    # Conversões explícitas para não depender da inferência de tipos do Pandas.
    data = pd.DataFrame(
        {
            "source_id": raw["id"].astype("string").str.strip(),
            "room_name": raw["room_id/id"].astype("string").str.strip(),
            "noted_date": pd.to_datetime(
                raw["noted_date"].astype("string").str.strip(),
                format="%d-%m-%Y %H:%M",
                errors="coerce",
            ),
            "temp": pd.to_numeric(raw["temp"], errors="coerce"),
            "out/in": raw["out/in"].astype("string").str.strip().str.title(),
        }
    )

    invalid = data.isna().any(axis=1)
    if invalid.any():
        examples = data.loc[invalid].head(5).to_string(index=False)
        raise ValueError(
            f"Foram encontradas {int(invalid.sum())} linhas com campos ausentes ou inválidos. "
            f"Nenhum dado foi carregado. Exemplos:\n{examples}"
        )

    engine = get_engine()
    create_table = """
    CREATE TABLE IF NOT EXISTS temperature_readings (
        reading_id BIGSERIAL PRIMARY KEY,
        source_id TEXT NOT NULL,
        room_name TEXT NOT NULL,
        noted_date TIMESTAMP NOT NULL,
        temp DOUBLE PRECISION NOT NULL,
        "out/in" TEXT NOT NULL
    );
    """

    print(f"Registros lidos: {len(data):,}".replace(",", "."))
    try:
        with engine.begin() as conn:
            conn.execute(text(create_table))
            # Truncar antes do carregamento evita duplicação em novas execuções.
            # source_id não é chave única: o CSV contém pelo menos um ID repetido.
            conn.execute(text("TRUNCATE TABLE temperature_readings RESTART IDENTITY"))

        data.to_sql(
            "temperature_readings",
            con=engine,
            if_exists="append",
            index=False,
            chunksize=2000,
            method="multi",
        )

        with engine.connect() as conn:
            count = conn.execute(
                text("SELECT COUNT(*) FROM temperature_readings")
            ).scalar_one()
            summary = conn.execute(
                text('SELECT "out/in", COUNT(*) FROM temperature_readings GROUP BY "out/in" ORDER BY "out/in"')
            ).all()

        print(f"Carga concluída. Registros no PostgreSQL: {count:,}".replace(",", "."))
        print("Leituras por categoria:")
        for category, total in summary:
            print(f"  {category}: {total:,}".replace(",", "."))
        print("Próxima etapa: python src/create_views.py")
    finally:
        engine.dispose()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        raise SystemExit(1)
