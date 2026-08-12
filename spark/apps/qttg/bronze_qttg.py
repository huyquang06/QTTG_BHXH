import argparse
import sys
from pyspark.sql import SparkSession
from schemas import MASTER_SCHEMA, DETAIL_SCHEMA

def main():
    parser = argparse.ArgumentParser(description="Bronze Layer Ingestion")
    parser.add_argument(
        "--input-dir",
        default="file:///opt/spark/data/raw_qttg_1m",
        help="Path to CSV File",
    )
    parser.add_argument(
        "--output-dir",
        default="file:///opt/spark/data/lake/bronze",
        help="Path to Parquet Broze File",
    )
    args = parser.parse_args()

    spark = (
        SparkSession.builder.appName("Bronze_Ingest_QTTG")
        .config("spark.sql.legacy.timeParserPolicy", "CORRECTED")
        .getOrCreate()
    )

    try: 
        #  Read CSV using Schema
        df_master = (
            spark.read.option("header", "true")
            .schema(MASTER_SCHEMA)
            .csv(f"{args.input_dir}/RAW_QTTG_BHXH.csv")
        )

        df_detail = (
            spark.read.option("header", "true")
            .schema(DETAIL_SCHEMA)
            .csv(f"{args.input_dir}/RAW_QTTG_BHXH_DETAIL.csv")
        )

        # Overwrite Parquet File
        master_out = f"{args.output_dir}/master"
        detail_out = f"{args.output_dir}/detail"

        df_master.write.mode("overwrite").parquet(master_out)
        df_detail.write.mode("overwrite").parquet(detail_out)

        # Count rows number in Parquet File
        master_count = spark.read.parquet(master_out).count()
        detail_count = spark.read.parquet(detail_out).count()

        # Check validable rows number
        if master_count != 142857 or detail_count != 1000000:
            raise ValueError(
                f"Invalid number of rows! Master: {master_count} (142857), Detail: {detail_count} (1000000)"
            )

        print(
            f"LAYER=BRONZE STATUS=SUCCESS MASTER_ROWS={master_count} DETAIL_ROWS={detail_count}"
        )

    except Exception as e: 
        print(f"LAYER=BRONZE STATUS=FAILED ERROR={str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()