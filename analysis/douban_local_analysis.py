import time
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "douban_movies.csv"
OUT = BASE / "outputs"
OUT.mkdir(exist_ok=True)


def font():
    return ImageFont.load_default()


def save_line_chart(points, path, title, x_label, y_label):
    width, height = 1000, 560
    margin_left, margin_right, margin_top, margin_bottom = 90, 40, 70, 80
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    fnt = font()
    xs = [float(x) for x, _ in points]
    ys = [float(y) for _, y in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    y_pad = max((max_y - min_y) * 0.08, 0.1)
    min_y -= y_pad
    max_y += y_pad

    x0, y0 = margin_left, height - margin_bottom
    x1, y1 = width - margin_right, margin_top
    draw.line([(x0, y0), (x1, y0)], fill="#111827", width=2)
    draw.line([(x0, y0), (x0, y1)], fill="#111827", width=2)
    draw.text((margin_left, 24), title, fill="#111827", font=fnt)
    draw.text((width // 2 - 40, height - 32), x_label, fill="#374151", font=fnt)
    draw.text((14, margin_top), y_label, fill="#374151", font=fnt)

    for i in range(6):
        y = y0 - (y0 - y1) * i / 5
        value = min_y + (max_y - min_y) * i / 5
        draw.line([(x0, y), (x1, y)], fill="#e5e7eb", width=1)
        draw.text((20, y - 7), f"{value:.1f}", fill="#4b5563", font=fnt)

    line = []
    for x, y in points:
        px = x0 + (float(x) - min_x) / (max_x - min_x) * (x1 - x0)
        py = y0 - (float(y) - min_y) / (max_y - min_y) * (y0 - y1)
        line.append((px, py))
    if len(line) >= 2:
        draw.line(line, fill="#2563eb", width=3)
    for px, py in line[:: max(1, len(line) // 14)]:
        draw.ellipse((px - 3, py - 3, px + 3, py + 3), fill="#2563eb")
    for i in range(6):
        x = x0 + (x1 - x0) * i / 5
        value = min_x + (max_x - min_x) * i / 5
        draw.text((x - 16, y0 + 10), f"{int(value)}", fill="#4b5563", font=fnt)
    image.save(path)


def save_bar_chart(labels, values, path, title, x_label):
    width, height = 1000, 560
    margin_left, margin_right, margin_top, margin_bottom = 170, 50, 70, 50
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    fnt = font()
    draw.text((margin_left, 24), title, fill="#111827", font=fnt)
    draw.text((width // 2 - 50, height - 30), x_label, fill="#374151", font=fnt)
    x0, y0 = margin_left, height - margin_bottom
    x1 = width - margin_right
    bar_area_h = y0 - margin_top
    max_value = max(values) if values else 1
    row_h = bar_area_h / max(len(values), 1)
    for i, (label, value) in enumerate(zip(labels, values)):
        y = margin_top + i * row_h + row_h * 0.18
        bar_h = row_h * 0.58
        bar_w = (value / max_value) * (x1 - x0)
        draw.text((20, y + 2), str(label)[:22], fill="#374151", font=fnt)
        draw.rectangle((x0, y, x0 + bar_w, y + bar_h), fill="#059669")
        draw.text((x0 + bar_w + 8, y + 2), f"{int(value)}", fill="#111827", font=fnt)
    draw.line([(x0, y0), (x1, y0)], fill="#111827", width=2)
    image.save(path)


def split_explode(df, column, output_column):
    tmp = df[["movie_id", "title", "year", "rating_score", "rating_count", column]].copy()
    tmp[column] = tmp[column].fillna("Unknown")
    tmp[output_column] = tmp[column].str.split("/")
    tmp = tmp.explode(output_column)
    tmp[output_column] = tmp[output_column].fillna("Unknown").str.strip()
    tmp = tmp[tmp[output_column] != ""]
    return tmp.drop(columns=[column])


start = time.perf_counter()
raw = pd.read_csv(DATA)
load_seconds = time.perf_counter() - start

for column in ["year", "rating_score", "rating_count", "collect_count"]:
    raw[column] = pd.to_numeric(raw[column], errors="coerce")

missing_ratio = raw.isna().mean().sort_values(ascending=False).reset_index()
missing_ratio.columns = ["column", "missing_ratio"]
missing_ratio.to_csv(OUT / "missing_ratio.csv", index=False, encoding="utf-8-sig")

rows_before = len(raw)
clean = raw.dropna(subset=["movie_id", "title", "year", "rating_score"]).copy()
clean = clean[(clean["rating_score"] > 0) & (clean["rating_count"] > 0)].copy()
clean["genres"] = clean["genres"].fillna("Unknown")
clean["countries"] = clean["countries"].fillna("Unknown")
clean["directors"] = clean["directors"].fillna("Unknown")
clean["summary"] = clean["summary"].fillna("")
rows_after = len(clean)

stats = clean[["year", "rating_score", "rating_count", "collect_count"]].describe().T
stats.to_csv(OUT / "basic_stats.csv", encoding="utf-8-sig")

genre_df = split_explode(clean, "genres", "genre")
country_df = split_explode(clean, "countries", "country")

query_start = time.perf_counter()
genre_top = (
    genre_df.groupby("genre")
    .agg(movie_count=("movie_id", "count"), avg_rating=("rating_score", "mean"))
    .sort_values(["movie_count", "avg_rating"], ascending=[False, False])
    .reset_index()
)
query_seconds = time.perf_counter() - query_start
genre_top.to_csv(OUT / "genre_top10.csv", index=False, encoding="utf-8-sig")

top_movies = clean.sort_values(["rating_score", "rating_count"], ascending=[False, False])[
    ["title", "year", "rating_score", "rating_count", "genres", "countries"]
].head(10)
top_movies.to_csv(OUT / "top_movies.csv", index=False, encoding="utf-8-sig")

yearly_trend = (
    clean.groupby("year")
    .agg(
        movie_count=("movie_id", "count"),
        avg_rating=("rating_score", "mean"),
        avg_rating_count=("rating_count", "mean"),
    )
    .query("movie_count >= 5")
    .reset_index()
    .sort_values("year")
)
yearly_trend.to_csv(OUT / "yearly_trend.csv", index=False, encoding="utf-8-sig")

movie_fact = clean[["movie_id", "title", "rating_score", "rating_count"]]
country_join = (
    movie_fact.merge(country_df[["movie_id", "country"]], on="movie_id", how="inner")
    .groupby("country")
    .agg(
        movie_count=("movie_id", "nunique"),
        avg_rating=("rating_score", "mean"),
        total_rating_count=("rating_count", "sum"),
    )
    .query("movie_count >= 20")
    .sort_values(["avg_rating", "movie_count"], ascending=[False, False])
    .reset_index()
)
country_join.to_csv(OUT / "country_join_top15.csv", index=False, encoding="utf-8-sig")

country_movie = movie_fact.merge(country_df[["movie_id", "country"]], on="movie_id", how="inner")
country_movie = country_movie.sort_values(
    ["country", "rating_score", "rating_count"], ascending=[True, False, False]
)
country_window = country_movie.groupby("country").head(1).sort_values(
    ["rating_score", "rating_count"], ascending=[False, False]
)
country_window.to_csv(OUT / "country_window_top.csv", index=False, encoding="utf-8-sig")

plot_years = yearly_trend[(yearly_trend["year"] >= 1980) & (yearly_trend["year"] <= 2025)]
save_line_chart(
    list(zip(plot_years["year"], plot_years["avg_rating"])),
    OUT / "yearly_rating_trend.png",
    "Douban average rating trend by year",
    "Year",
    "Average rating",
)

top_genres = genre_top.head(10)
save_bar_chart(
    list(top_genres["genre"]),
    list(top_genres["movie_count"]),
    OUT / "genre_top10.png",
    "Top 10 genres by movie count",
    "Movie count",
)

performance = pd.DataFrame(
    [
        {"engine": "Pandas local", "workers": 1, "seconds": round(query_seconds, 4)},
        {"engine": "PySpark on CCE", "workers": 1, "seconds": None},
        {"engine": "PySpark on CCE", "workers": 2, "seconds": None},
    ]
)
performance.to_csv(OUT / "performance_template.csv", index=False, encoding="utf-8-sig")

summary = {
    "rows_before": rows_before,
    "rows_after": rows_after,
    "dropped_rows": rows_before - rows_after,
    "load_seconds": round(load_seconds, 4),
    "pandas_groupby_seconds": round(query_seconds, 4),
    "rating_mean": round(clean["rating_score"].mean(), 4),
    "rating_min": round(clean["rating_score"].min(), 4),
    "rating_max": round(clean["rating_score"].max(), 4),
}
pd.DataFrame([summary]).to_csv(OUT / "analysis_summary.csv", index=False, encoding="utf-8-sig")

print(summary)
print("Wrote outputs to", OUT)
