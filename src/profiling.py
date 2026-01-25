from __future__ import annotations
import polars as pl

def schema_overview(df: pl.DataFrame) -> pl.DataFrame:
    rows = []
    for name, dtype in df.schema.items():
        s = df.get_column(name)
        rows.append(
            {
                "column": name,
                "dtype": str(dtype),
                "nulls": int(s.null_count()),
                "unique": int(s.n_unique()),
            }
        )
    return pl.DataFrame(rows)

def numeric_summary(df: pl.DataFrame, col: str) -> dict:
    s = df.get_column(col)
    out = {
        "count": int(s.len()),
        "nulls": int(s.null_count()),
    }
    # Polars will error if non-numeric; caller should check dtype
    desc = s.describe()
    # describe returns a small df: statistic + value
    stats = {r[0]: r[1] for r in desc.rows()}
    # normalize keys a bit
    out.update(
        {
            "mean": stats.get("mean"),
            "std": stats.get("std"),
            "min": stats.get("min"),
            "max": stats.get("max"),
            "median": stats.get("50%"),
        }
    )
    return out

def top_values(df: pl.DataFrame, col: str, top_n: int = 20) -> pl.DataFrame:
    return (
        df.select(pl.col(col))
        .with_columns(pl.col(col).cast(pl.Utf8, strict=False))
        .group_by(col)
        .len()
        .sort("len", descending=True)
        .head(top_n)
    )

def histogram(df: pl.DataFrame, col: str, bins: int = 40) -> pl.DataFrame:
    """
    Returns bin_left, bin_right, count for numeric col.
    """
    s = df.get_column(col).drop_nulls()
    if s.len() == 0:
        return pl.DataFrame({"bin_left": [], "bin_right": [], "count": []})

    mn = float(s.min())
    mx = float(s.max())
    if mn == mx:
        return pl.DataFrame({"bin_left": [mn], "bin_right": [mx], "count": [int(s.len())]})

    width = (mx - mn) / bins
    # compute bin index
    b = ((pl.col(col) - mn) / width).floor().cast(pl.Int64).clip(0, bins - 1)
    tmp = df.select([pl.col(col), b.alias("__bin")]).drop_nulls()
    counts = tmp.group_by("__bin").len().sort("__bin")
    # produce edges
    edges = pl.DataFrame({"__bin": list(range(bins))}).join(counts, on="__bin", how="left").fill_null(0)
    edges = edges.with_columns(
        (mn + pl.col("__bin") * width).alias("bin_left"),
        (mn + (pl.col("__bin") + 1) * width).alias("bin_right"),
        pl.col("len").alias("count"),
    ).select(["bin_left", "bin_right", "count"])
    return edges
