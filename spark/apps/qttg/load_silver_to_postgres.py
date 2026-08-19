import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat, lit

def main():
        # 1. Khởi tạo Spark Session
    spark = SparkSession.builder \
        .appName("Load_Silver_To_Postgres") \
        .getOrCreate()

        # Cấu hình JDBC kết nối Postgres
    jdbc_url = "jdbc:postgresql://postgres:5432/airflow"
    db_properties = {
        "user": "airflow",
        "password": "airflow",
        "driver": "org.postgresql.Driver"
    }

    try:
        print("Đang đọc dữ liệu Parquet từ Silver Layer...")
        df_master = spark.read.parquet("file:///opt/spark/data/lake/silver/master")
        df_detail = spark.read.parquet("file:///opt/spark/data/lake/silver/detail")

            # 2. Lọc và chuẩn hóa dữ liệu Master
        df_master_clean = df_master \
            .filter(col("IS_DELETED") == 0) \
            .withColumn("full_name", concat(lit("Người lao động "), col("NLD_ID"))) \
            .select(
                col("ID").alias("id"),
                col("NLD_ID").alias("nld_id"),
                col("SO_SO_BHXH").alias("so_so_bhxh"),
                col("full_name"),
                col("THANG_BD").alias("thang_bd"),
                col("THANG_KT").alias("thang_kt")
            )

            # 3. Chuẩn hóa Detail
        df_detail_clean = df_detail.select(
            col("ID").alias("id"),
            col("MASTER_ID").alias("master_id"),
            col("NLD_ID").alias("nld_id"),
            col("TU_THANG").alias("tu_thang"),
            col("DEN_THANG").alias("den_thang"),
            col("MA_DON_VI").alias("ma_don_vi"),
            col("TEN_DON_VI").alias("ten_don_vi"),
            col("MUC_LUONG").alias("muc_luong")
        )

        print("Đang kết nối để Truncate dữ liệu cũ trong Postgres...")
            # Lấy ClassLoader của Spark để load Driver Postgres
        jvm = spark._jvm
        classloader = jvm.java.lang.Thread.currentThread().getContextClassLoader()
        driver_class = classloader.loadClass("org.postgresql.Driver")

            # Khởi tạo instance của Driver trực tiếp để tránh lỗi ClassNotFound từ DriverManager
        driver_instance = driver_class.newInstance()
            # Cấu hình thuộc tính kết nối
        props = jvm.java.util.Properties()
        props.setProperty("user", db_properties["user"])
        props.setProperty("password", db_properties["password"])

            # Tạo kết nối trực tiếp
        conn = driver_instance.connect(jdbc_url, props)

        stmt = conn.createStatement()
        # Truncate CASCADE giúp xóa sạch dữ liệu cũ kể cả khi có ràng buộc khóa ngoại
        stmt.execute("TRUNCATE TABLE qttg_bhxh_detail CASCADE")
        stmt.execute("TRUNCATE TABLE qttg_bhxh CASCADE")
        conn.close()
        print("Đã dọn dẹp bảng trống thành công!")

            # 4. Ghi dữ liệu vào Postgres
        print("Đang nạp dữ liệu vào bảng qttg_bhxh (Master)...")
        df_master_clean.write \
            .jdbc(url=jdbc_url, table="qttg_bhxh", mode="append", properties=db_properties)

        print("Đang nạp dữ liệu vào bảng qttg_bhxh_detail (Detail)...")
        df_detail_clean.write \
            .jdbc(url=jdbc_url, table="qttg_bhxh_detail", mode="append", properties=db_properties)

        print("LAYER=POSTGRES STATUS=SUCCESS")

    except Exception as e:
        print(f"LAYER=POSTGRES STATUS=FAILED ERROR={str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        spark.stop()

if __name__ == "__main__":
        main()