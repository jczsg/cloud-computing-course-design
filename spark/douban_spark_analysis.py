import os
import time

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window


INPUT_PATH = os.environ.get("INPUT_PATH", "file:///opt/spark/work-dir/douban_movies.csv")
OUTPUT_PATH = os.environ.get("OUTPUT_PATH", "file:///tmp/douban-output")


spark = SparkSession.builder.appName("douban-movie-analysis").getOrCreate()
job_start = time.perf_counter()

raw = (
    spark.read.option("header", True)
    .option("multiLine", True)
    .option("escape", '"')
    .csv(INPUT_PATH)
)

print("=== Raw schema ===")
raw.printSchema()
print("=== Raw sample ===")
raw.show(5, truncate=False)

total = raw.count()
missing_rows = []
for column in raw.columns:
    missing = raw.filter(F.col(column).isNull() | (F.trim(F.col(column)) == "")).count()
    missing_rows.append((column, missing, missing / total if total else 0.0))

missing_df = spark.createDataFrame(missing_rows, ["column", "missing_count", "missing_ratio"])
missing_df.orderBy(F.desc("missing_ratio")).show(truncate=False)

typed = (
    raw.withColumn("year_int", F.col("year").cast("double").cast("int"))
    .withColumn("rating_score_d", F.col("rating_score").cast("double"))
    .withColumn("rating_count_l", F.col("rating_count").cast("long"))
    .withColumn("collect_count_l", F.col("collect_count").cast("long"))
)

clean = (
    typed.dropna(subset=["movie_id", "title", "year_int", "rating_score_d"])
    .filter((F.col("rating_score_d") > 0) & (F.col("rating_count_l") > 0))
    .fillna({"genres": "Unknown", "countries": "Unknown", "directors": "Unknown", "summary": ""})
)

print("Rows before cleaning:", total)
print("Rows after cleaning:", clean.count())
clean.select("year_int", "rating_score_d", "rating_count_l", "collect_count_l").describe().show()

genre_df = clean.select(
    "movie_id",
    "title",
    "year_int",
    "rating_score_d",
    "rating_count_l",
    F.explode(F.split(F.col("genres"), "/")).alias("genre"),
)

country_df = clean.select(
    "movie_id",
    "title",
    F.explode(F.split(F.col("countries"), "/")).alias("country"),
)

print("=== Query 1: GROUP BY genre ===")
q1 = (
    genre_df.groupBy("genre")
    .agg(
        F.count("*").alias("movie_count"),
        F.round(F.avg("rating_score_d"), 3).alias("avg_rating"),
    )
    .orderBy(F.desc("movie_count"))
)
q1.show(10, truncate=False)

print("=== Query 2: ORDER BY Top-N movies ===")
q2 = (
    clean.select("title", "year_int", "rating_score_d", "rating_count_l", "genres")
    .orderBy(F.desc("rating_score_d"), F.desc("rating_count_l"))
    .limit(10)
)
q2.show(truncate=False)

print("=== Query 3: yearly rating trend ===")
q3 = (
    clean.groupBy("year_int")
    .agg(
        F.count("*").alias("movie_count"),
        F.round(F.avg("rating_score_d"), 3).alias("avg_rating"),
        F.round(F.avg("rating_count_l"), 1).alias("avg_rating_count"),
    )
    .filter(F.col("movie_count") >= 5)
    .orderBy("year_int")
)
q3.show(40, truncate=False)

print("=== Query 4: JOIN movie facts with country explode ===")
movie_fact = clean.select("movie_id", "title", "rating_score_d", "rating_count_l")
q4 = (
    movie_fact.join(country_df.select("movie_id", "country"), on="movie_id", how="inner")
    .groupBy("country")
    .agg(
        F.countDistinct("movie_id").alias("movie_count"),
        F.round(F.avg("rating_score_d"), 3).alias("avg_rating"),
        F.sum("rating_count_l").alias("total_rating_count"),
    )
    .filter(F.col("movie_count") >= 20)
    .orderBy(F.desc("avg_rating"), F.desc("movie_count"))
)
q4.show(15, truncate=False)

print("=== Query 5: window top movie by country ===")
country_movie = movie_fact.join(country_df.select("movie_id", "country"), "movie_id")
window = Window.partitionBy("country").orderBy(F.desc("rating_score_d"), F.desc("rating_count_l"))
q5 = (
    country_movie.withColumn("rank_in_country", F.row_number().over(window))
    .filter(F.col("rank_in_country") == 1)
    .select("country", "title", "rating_score_d", "rating_count_l")
    .orderBy(F.desc("rating_score_d"), F.desc("rating_count_l"))
)
q5.show(20, truncate=False)

q1.coalesce(1).write.mode("overwrite").option("header", True).csv(f"{OUTPUT_PATH}/genre_top")
q2.coalesce(1).write.mode("overwrite").option("header", True).csv(f"{OUTPUT_PATH}/top_movies")
q3.coalesce(1).write.mode("overwrite").option("header", True).csv(f"{OUTPUT_PATH}/yearly_trend")
q4.coalesce(1).write.mode("overwrite").option("header", True).csv(f"{OUTPUT_PATH}/country_join")
q5.coalesce(1).write.mode("overwrite").option("header", True).csv(f"{OUTPUT_PATH}/country_window")

print(f"TOTAL_SECONDS={time.perf_counter() - job_start:.3f}")
spark.stop()
