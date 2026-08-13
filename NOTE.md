# QTTG Spark ETL

Du an nay xu ly du lieu QTTG BHXH bang PySpark theo mo hinh nhiều tang trong data lake.
Muc tieu la doc du lieu raw CSV, lam sach va chuan hoa du lieu, sau do tong hop bao cao theo thang va kiem tra tinh toan ven cua ket qua.

## Cau truc xu ly

- `schemas.py`: Khai bao schema cho 2 file raw `RAW_QTTG_BHXH.csv` va `RAW_QTTG_BHXH_DETAIL.csv`.
- `bronze_qttg.py`: Doc CSV theo schema, kiem tra so dong dau vao, ghi du lieu goc sang tang Bronze.
- `silver_qttg.py`: Lam sach truong du lieu, soft-delete ban ghi master cu, va join detail voi master dang active.
- `gold_qttg.py`: Sinh danh sach thang, mo rong detail theo khoang thang, tong hop chi tieu bao cao theo `THANG_ID`.
- `validate_qttg.py`: Kiem tra cac rule chat luong du lieu sau ETL.
- `qttg_test.ipynb`: Notebook de test logic tung tang trong Jupyter.

## Cac rule chinh

- Bronze phai dung so dong ky vong:
- `master = 142857`
- `detail = 1000000`
- Silver chi giu 1 ban ghi master active moi `SO_SO_BHXH`.
- Silver detail khong duoc mo coi va phai co `TU_THANG <= DEN_THANG`.
- Gold khong duoc trung `THANG_ID`.

## Cach chay

Tat ca script hien dung `argparse` voi tham so bat buoc.

Vi du:

```bash
python bronze_qttg.py --input-dir C:/Users/thinkbook123/Datahub/output/raw_qttg_1m --output-dir C:/Users/thinkbook123/Datahub/output/lake/bronze
python silver_qttg.py --input-dir C:/Users/thinkbook123/Datahub/output/lake/bronze --output-dir C:/Users/thinkbook123/Datahub/output/lake/silver
python gold_qttg.py --input-dir C:/Users/thinkbook123/Datahub/output/lake/silver --output-dir C:/Users/thinkbook123/Datahub/output/lake/gold
python validate_qttg.py --lake-dir C:/Users/thinkbook123/Datahub/output/lake
```

## Ghi chu test

- Neu test bang Jupyter tren Windows, uu tien dung `qttg_test.ipynb`.
- Notebook duoc thiet ke de test logic tren DataFrame trong bo nho, tranh loi `HADOOP_HOME` khi ghi parquet local.
- Khi can test end-to-end ghi file that, nen chay bang `spark-submit` hoac moi truong Spark da cau hinh day du.
