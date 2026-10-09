"""Cria/atualiza as três views SQL usadas pelo dashboard."""
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def main() -> int:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL não definida. Configure o arquivo .env.")
    sql_path = ROOT / "sql" / "views.sql"
    sql_text = sql_path.read_text(encoding="utf-8")
    statements = [part.strip() for part in sql_text.split(";") if part.strip()]
    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        with engine.begin() as conn:
            for statement in statements:
                conn.execute(text(statement))
        print(f"Views criadas/atualizadas a partir de {sql_path}:")
        with engine.connect() as conn:
            for view_name in (
                "avg_temp_por_categoria",
                "leituras_por_hora",
                "temp_max_min_por_dia",
            ):
                rows = conn.execute(text(f"SELECT COUNT(*) FROM {view_name}")).scalar_one()
                print(f"  {view_name}: {rows} linha(s)")
    finally:
        engine.dispose()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        raise SystemExit(1)
