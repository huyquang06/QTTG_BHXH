## schemas.py

- File được tạo ra với mục đích gán kiểu dữ liệu cho 2 schema load từ CSV: **MASTER_SCHEMA** và **DETAIL_SCHEMA**.

- Từ 2 file DDL: **DDL_RAW_QTTG_BHXH.sql** và **DDL_RAW_QTTG_BHXH_DETAIL.sql**, xác định được các kiểu dữ liệu chính để load vào schema là: **LongType**, **StringType**, **IntegerType**, **DecimalType**.

- VARCHAR2 & TIMESTAMP: Chuyển thành **StringType()** ở Bronze layer để tránh văng lỗi khi parse chuỗi ngày tháng CSV chưa chuẩn hóa.  

## bronze_qttg.py

- Sau khi có kiểu dữ liệu từ **schema.py**, import vào file: *"from schemas import MASTER_SCHEMA, DETAIL_SCHEMA"*.

- Sử dụng lib *"argparse"* để xử lý tham số truyền vào (đường dẫn, tên file,...)

- Sử dụng *"try-catch"* để kiểm soát việc đếm số dòng, không hợp lệ (sai yêu cầu đề bài) thì print ra log, đúng thì print success.

## silver_qttg.py

- Sử dụng thêm lib Window để xử lý các câu lệnh SQL (phần lọc dòng có CREATED_AT mới nhất và join vào bảng df_bronze_detail).