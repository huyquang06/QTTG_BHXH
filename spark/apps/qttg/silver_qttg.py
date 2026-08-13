import argparse
import sys

from pyspark.sql import SparkSession
from pyspark.sql.functions import coalesce, col, lit, regexp_replace, row_number, trim, when
from pyspark.sql.window import Window


def main():
    parser = argparse.ArgumentParser(description="Silver Layer Processing")
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Đường dẫn chứa Parquet Bronze",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Đường dẫn ghi Parquet Silver",
    )
    args = parser.parse_args()

    spark = (
        SparkSession.builder.appName("Silver_Transform_QTTG")
        .config("spark.sql.legacy.timeParserPolicy", "CORRECTED")
        .getOrCreate()
    )

    try:
        df_bronze_master = spark.read.parquet(f"{args.input_dir}/master")
        df_bronze_detail = spark.read.parquet(f"{args.input_dir}/detail")

        # lam sach cho bronze master
        df_cleaned_master = (
            df_bronze_master.withColumn("SO_SO_BHXH", trim(col("SO_SO_BHXH")))
            .withColumn("THANG_BD", regexp_replace(col("THANG_BD"), r"[^0-9]", ""))
            .withColumn("THANG_KT", regexp_replace(col("THANG_KT"), r"[^0-9]", ""))
        )

        window_spec = Window.partitionBy("SO_SO_BHXH").orderBy(
            col("CREATED_AT").desc(), col("ID").desc()
        )
        df_silver_master = (
            df_cleaned_master.withColumn("rn", row_number().over(window_spec))
            .withColumn("IS_DELETED", when(col("rn") == 1, 0).otherwise(1))
            .drop("rn")
        )

        # lam sach cho bronze detail
        df_cleaned_detail = (
            df_bronze_detail.withColumn("MA_DON_VI", trim(col("MA_DON_VI")))
            .withColumn("TU_THANG", regexp_replace(col("TU_THANG"), r"[^0-9]", ""))
            .withColumn("DEN_THANG", regexp_replace(col("DEN_THANG"), r"[^0-9]", ""))
            .withColumn("MUC_LUONG", coalesce(col("MUC_LUONG"), lit(0)))
        )

        df_active_master = df_silver_master.filter(col("IS_DELETED") == 0).select(
            col("ID").alias("M_ID"), col("NLD_ID").alias("M_NLD_ID")
        )
        df_silver_detail = df_cleaned_detail.join(
            df_active_master,
            (df_cleaned_detail["MASTER_ID"] == df_active_master["M_ID"])
            & (df_cleaned_detail["NLD_ID"] == df_active_master["M_NLD_ID"]),
            "inner",
        ).drop("M_ID", "M_NLD_ID")

        master_out = f"{args.output_dir}/master"
        detail_out = f"{args.output_dir}/detail"
        df_silver_master.write.mode("overwrite").parquet(master_out)
        df_silver_detail.write.mode("overwrite").parquet(detail_out)

        person_rows = (
            spark.read.parquet(master_out).filter(col("IS_DELETED") == 0).count()
        )
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
