"""Генерирует схему БД из моделей SQLAlchemy:
  docs/er-diagram.md  - ER-диаграмма Mermaid (GitHub рисует её прямо на странице)
  docs/schema.dbml    - для импорта в dbdiagram.io
  docs/schema.sql     - SQL для импорта в drawSQL

Запуск из папки backend:  python scripts/export_schema.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import Boolean, Date, DateTime, Enum, Integer, Numeric, String, Text  # noqa: E402
from sqlalchemy.dialects import postgresql  # noqa: E402
from sqlalchemy.schema import CreateTable  # noqa: E402

import app.models  # noqa: E402,F401
from app.database import Base  # noqa: E402

DOCS = Path(__file__).resolve().parents[2] / "docs"
tables = Base.metadata.sorted_tables


def fk_columns(table):
    return {fk.parent.name for fk in table.foreign_keys}


def mermaid_type(col_type):
    if isinstance(col_type, Enum):
        return "enum"
    if isinstance(col_type, Text):
        return "text"
    if isinstance(col_type, String):
        return "string"
    if isinstance(col_type, Boolean):
        return "bool"
    if isinstance(col_type, DateTime):
        return "datetime"
    if isinstance(col_type, Date):
        return "date"
    if isinstance(col_type, Numeric):
        return "decimal"
    if isinstance(col_type, Integer):
        return "int"
    return "string"


def dbml_type(col_type):
    if isinstance(col_type, Enum):
        return f"varchar({col_type.length})"
    if isinstance(col_type, Text):
        return "text"
    if isinstance(col_type, String):
        return f"varchar({col_type.length})" if col_type.length else "varchar"
    if isinstance(col_type, Boolean):
        return "boolean"
    if isinstance(col_type, DateTime):
        return "timestamp"
    if isinstance(col_type, Date):
        return "date"
    if isinstance(col_type, Numeric):
        return f"decimal({col_type.precision},{col_type.scale})"
    if isinstance(col_type, Integer):
        return "integer"
    return "varchar"


def build_mermaid():
    lines = ["erDiagram"]
    for table in tables:
        for fk in table.foreign_keys:
            parent = fk.column.table.name
            col = fk.parent
            left = "|o" if col.nullable else "||"
            right = "o|" if col.unique else "o{"
            lines.append(f'    {parent} {left}--{right} {table.name} : "{col.name}"')
    for table in tables:
        fks = fk_columns(table)
        lines.append(f"    {table.name} {{")
        for col in table.columns:
            keys = []
            if col.primary_key:
                keys.append("PK")
            if col.name in fks:
                keys.append("FK")
            if col.unique and not col.primary_key:
                keys.append("UK")
            suffix = f" {', '.join(keys)}" if keys else ""
            lines.append(f"        {mermaid_type(col.type)} {col.name}{suffix}")
        lines.append("    }")
    return "\n".join(lines)


def build_dbml():
    out = []
    for table in tables:
        out.append(f"Table {table.name} {{")
        for col in table.columns:
            attrs = []
            if col.primary_key:
                attrs += ["pk", "increment"]
            else:
                if not col.nullable:
                    attrs.append("not null")
                if col.unique:
                    attrs.append("unique")
            if isinstance(col.type, Enum):
                attrs.append(f"note: '{' | '.join(col.type.enums)}'")
            suffix = f" [{', '.join(attrs)}]" if attrs else ""
            out.append(f"  {col.name} {dbml_type(col.type)}{suffix}")
        out.append("}\n")
    for table in tables:
        for fk in table.foreign_keys:
            arrow = "-" if fk.parent.unique else ">"
            out.append(f"Ref: {table.name}.{fk.parent.name} {arrow} {fk.column.table.name}.{fk.column.name}")
    return "\n".join(out) + "\n"


def build_sql():
    dialect = postgresql.dialect()
    return "\n".join(str(CreateTable(t).compile(dialect=dialect)).strip() + ";\n" for t in tables)


def main():
    DOCS.mkdir(exist_ok=True)
    er = (
        "# ER-диаграмма CampusGear\n\n"
        f"Таблиц: {len(tables)}. Диаграмма генерируется из моделей командой "
        "`python scripts/export_schema.py`.\n\n"
        f"```mermaid\n{build_mermaid()}\n```\n"
    )
    (DOCS / "er-diagram.md").write_text(er, encoding="utf-8")
    (DOCS / "schema.dbml").write_text(build_dbml(), encoding="utf-8")
    (DOCS / "schema.sql").write_text(build_sql(), encoding="utf-8")
    print(f"Готово: {len(tables)} таблиц -> {DOCS}")


if __name__ == "__main__":
    main()
