import argparse
import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import col


def main():
    parser = argparse.ArgumentParser(description="Validate ETL Lake Layers")
    parser.add_argument(
        "--lake-dir",
        required=True,
        help="Đường dẫn thư mục gốc Data Lake",
    )
    args = parser.parse_args()

    spark = (
        SparkSession.builder.appName("Validate_QTTG_Lake")
        .config("spark.sql.legacy.timeParserPolicy", "CORRECTED")
        .getOrCreate()
    )

    error_logs = []

    try:
        lake_dir = args.lake_dir.rstrip("/")
        silver_master = spark.read.parquet(f"{lake_dir}/silver/master")
        silver_detail = spark.read.parquet(f"{lake_dir}/silver/detail")
        gold_df = spark.read.parquet(f"{lake_dir}/gold")

        # 1. Kiểm tra detail không mồ côi (Master ID phải tồn tại ở Silver Master)
        orphan_details = silver_detail.join(
            silver_master,
            silver_detail["MASTER_ID"] == silver_master["ID"],
            "left_anti",
        ).count()

        if orphan_details > 0:
            error_logs.append(
                f"Phát hiện {orphan_details} dòng detail mồ côi!"
            )

        # 2. Kiểm tra mỗi người chỉ còn đúng 1 master tại Silver
        duplicate_persons = (
            silver_master.filter(col("IS_DELETED") == 0)
            .groupBy("SO_SO_BHXH")
            .count()
            .filter(col("count") > 1)
            .count()
        )

        if duplicate_persons > 0:
            error_logs.append(
                f"Phát hiện {duplicate_persons} người bị trùng lặp master ở Silver!"
            )

        # 3. Kiểm tra TU_THANG <= DEN_THANG tại Silver Detail
        invalid_month_range = silver_detail.filter(
            col("TU_THANG") > col("DEN_THANG")
        ).count()

        if invalid_month_range > 0:
            error_logs.append(
                f"Phát hiện {invalid_month_range} dòng detail có TU_THANG > DEN_THANG!"
            )

        # 4. Kiểm tra Gold không trùng tháng (THANG_ID là duy nhất)
        duplicate_gold_months = (
            gold_df.groupBy("THANG_ID")
            .count()
            .filter(col("count") > 1)
            .count()
        )

        if duplicate_gold_months > 0:
            error_logs.append(
                f"Phát hiện {duplicate_gold_months} tháng bị trùng lặp ở tầng Gold!"
            )

        # Báo lỗi nếu có bất kỳ vi phạm nào
        if len(error_logs) > 0:
            error_summary = " | ".join(error_logs)
            raise ValueError(f"VALIDATION FAILED: {error_summary}")

        print("LAYER=VALIDATE STATUS=SUCCESS ERROR_ROWS=0", flush=True)
        sys.stdout.flush()

    except Exception as e:
        print(
            f"LAYER=VALIDATE STATUS=FAILED ERROR={str(e)}",
            file=sys.stderr,
            flush=True,
        )
        sys.stderr.flush()
        sys.exit(1)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
