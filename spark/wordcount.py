from pyspark.sql import SparkSession


spark = SparkSession.builder.appName("cloud-course-wordcount").getOrCreate()

data = [
    "hello spark",
    "hello cloud computing",
    "spark on kubernetes",
    "cloud data spark",
]

result = (
    spark.sparkContext.parallelize(data)
    .flatMap(lambda line: line.split())
    .map(lambda word: (word, 1))
    .reduceByKey(lambda a, b: a + b)
    .takeOrdered(10, key=lambda x: -x[1])
)

print("Top 10 words:", result)
spark.stop()
