from __future__ import annotations
import json
import os
import polars as pl

# --- Feature definition format (safe) ---
# {
#   "name": "debt_to_income",
#   "kind": "binary_op",
#   "op": "/",
#   "a": "debt",
#   "b": "income",
#   "guard": "b_gt_zero" | None,
#   "fill_null": None | number
# }

def compile_feature_expr(f: dict) -> pl.Expr:
    name = f["name"]
    kind = f["kind"]

    if kind == "binary_op":
        a = pl.col(f["a"])
        b = pl.col(f["b"])
        op = f["op"]
        guard = f.get("guard")
        fill_null = f.get("fill_null", None)

        expr = None
        if op == "/":
            expr = a / b
        elif op == "*":
            expr = a * b
        elif op == "+":
            expr = a + b
        elif op == "-":
            expr = a - b
        else:
            raise ValueError(f"Unsupported op: {op}")

        if guard == "b_gt_zero":
            expr = pl.when(b > 0).then(expr).otherwise(None)

        if fill_null is not None:
            expr = expr.fill_null(fill_null)

        return expr.alias(name)

    raise ValueError(f"Unsupported kind: {kind}")

def apply_features(df: pl.DataFrame, features: list[dict]) -> pl.DataFrame:
    if not features:
        return df
    exprs = [compile_feature_expr(f) for f in features]
    return df.with_columns(exprs)

def save_features(features: list[dict], path: str = "artifacts/features.json") -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fp:
        json.dump(features, fp, indent=2, ensure_ascii=False)

def load_features(path: str = "artifacts/features.json") -> list[dict]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fp:
        return json.load(fp)
