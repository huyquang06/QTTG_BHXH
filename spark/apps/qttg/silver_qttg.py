import argparse
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, row_number
from pyspark.sql.window import Window


def main():
    parser = argparse.ArgumentParser(description="Silver Layer Processing")
    parser.add_argument(
        "--input-dir",
        default="file:///opt/spark/data/lake/bronze",
        help="Đường dẫn chứa Parquet Bronze",
    )
    parser.add_argument(
        "--output-dir",
        default="file:///opt/spark/data/lake/silver",
        help="Đường dẫn ghi Parquet Silver",
    )
    args = parser.parse_args()

    spark = (
        SparkSession.builder.appName("Silver_Transform_QTTG")
        .config("spark.sql.legacy.timeParserPolicy", "CORRECTED")
        .getOrCreate()
    )

    try:
        # 1. Đọc dữ liệu từ Bronze Lake
        df_bronze_master = spark.read.parquet(f"{args.input_dir}/master")
        df_bronze_detail = spark.read.parquet(f"{args.input_dir}/detail")

        # 2. Định nghĩa Window Spec để chọn bản ghi mới nhất của mỗi người
        window_spec = Window.partitionBy("SO_SO_BHXH").orderBy(
            col("CREATED_AT").desc(), col("ID").desc()
        )

        # 3. Đánh số thứ tự và chỉ giữ bản ghi mới nhất (rn = 1)
        df_silver_master = (
            df_bronze_master.withColumn("rn", row_number().over(window_spec))
            .filter(col("rn") == 1)
            .drop("rn")
        )

        # 4. Lọc Detail chỉ thuộc về các MASTER_ID mới nhất
        df_latest_ids = df_silver_master.select(
            col("ID").alias("LATEST_MASTER_ID")
        )

        df_silver_detail = df_bronze_detail.join(
            df_latest_ids,
            df_bronze_detail["MASTER_ID"] == df_latest_ids["LATEST_MASTER_ID"],
            "inner",
        ).drop("LATEST_MASTER_ID")

        # 5. Ghi đè kết quả ra Silver Lake dạng Parquet
        master_out = f"{args.output_dir}/master"
        detail_out = f"{args.output_dir}/detail"

        df_silver_master.write.mode("overwrite").parquet(master_out)
        df_silver_detail.write.mode("overwrite").parquet(detail_out)

        # 6. Kiểm tra đếm dòng và xuất Log
        person_rows = spark.read.parquet(master_out).count()
        detail_rows = spark.read.parquet(detail_out).count()

        print(
            f"LAYER=SILVER STATUS=SUCCESS PERSON_ROWS={person_rows} DETAIL_ROWS={detail_rows}"
        )

    except Exception as e:
        print(f"LAYER=SILVER STATUS=FAILED ERROR={str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()