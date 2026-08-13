import argparse
import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    avg,
    col,
    countDistinct,
    date_format,
    explode,
    expr,
    max as spark_max,
    min as spark_min,
    sequence,
    sum as spark_sum,
    to_date,
    when,
)


def main():
    parser = argparse.ArgumentParser(description="Gold Layer Processing")
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Path to Parquet Silver",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Path to Parquet Gold",
    )
    args = parser.parse_args()

    spark = (
        SparkSession.builder.appName("Gold_Monthly_Report_QTTG")
        .config("spark.sql.legacy.timeParserPolicy", "CORRECTED")
        .getOrCreate()
    )

    try:
        df_silver_master = spark.read.parquet(f"{args.input_dir}/master")
        df_silver_detail = spark.read.parquet(f"{args.input_dir}/detail")

        df_range = df_silver_detail.agg(
            spark_min(to_date(col("TU_THANG"), "yyyyMM")).alias("min_date"),
            spark_max(to_date(col("DEN_THANG"), "yyyyMM")).alias("max_date"),
        )

        df_dim_thang = (
            df_range.select(
                explode(
                    sequence(
                        col("min_date"),
                        col("max_date"),
                        expr("interval 1 month"),
                    )
                ).alias("month_date")
            )
            .select(date_format(col("month_date"), "yyyyMM").alias("THANG_ID"))
        )

        df_month_detail = df_dim_thang.join(
            df_silver_detail,
            (col("THANG_ID") >= df_silver_detail["TU_THANG"])
            & (col("THANG_ID") <= df_silver_detail["DEN_THANG"]),
            "inner",
        )

        df_joined = df_month_detail.join(
            df_silver_master.filter(col("IS_DELETED") == 0).select(
                col("ID").alias("M_ID"), col("SO_SO_BHXH")
            ),
            df_month_detail["MASTER_ID"] == col("M_ID"),
            "inner",
        )

        df_gold = df_joined.groupBy("THANG_ID").agg(
            countDistinct("SO_SO_BHXH").alias("SO_NGUOI_THAM_GIA"),
            countDistinct("MA_DON_VI").alias("SO_DON_VI"),
            spark_sum("MUC_LUONG").alias("TONG_QUY_LUONG"),
            avg(when(col("MUC_LUONG") > 0, col("MUC_LUONG"))).alias(
                "LUONG_BINH_QUAN"
            ),
            countDistinct(when(col("MUC_LUONG") == 0, col("SO_SO_BHXH"))).alias(
                "SO_NGUOI_LUONG_0"
            ),
        )

        df_gold.write.mode("overwrite").parquet(args.output_dir)

        df_gold_result = spark.read.parquet(args.output_dir)
        report_rows = df_gold_result.count()

        print(
            "\n--- BẢNG BÁO CÁO MẪU TẦNG GOLD (20 THÁNG ĐẦU TIÊN) ---",
            flush=True,
        )
        df_gold_result.orderBy("THANG_ID").show(20, truncate=False)

        print(f"LAYER=GOLD STATUS=SUCCESS REPORT_ROWS={report_rows}", flush=True)
        sys.stdout.flush()

    except Exception as e:
        print(f"LAYER=GOLD STATUS=FAILED ERROR={str(e)}", file=sys.stderr)
        sys.stderr.flush()
        sys.exit(1)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
