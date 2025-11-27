Module nay chiu trach nhiem cho cac tac vu xu ly dinh ky, khoi luong lon.

- Cac chuc nang chinh:
   1. Lam sach du lieu : Xu ly cac gia tri thieu , ngoai le(outliers) va dinh dang du lieu
   2. Chuyen doi du lieu : Thuc hien cac phep tinh va chuyen doi phuc tap.
   3. Tong hop va luu tru : Tao ra cac bo du lieu tong hop (aggregated dataset) 
   4. Tao cac bao cao thong ke dinh ky ve thi truong

- Huong dan van hanh va trien khai
   1. # Tao moi truong ao
      python3 -m venv .venv
      source .venv/bin/activate

      # Cài đặt các thư viện cần thiết
      pip install -r requirements.txt
   2. Cau hinh bien moi truong
      Cau hinh trong file .env
      SPARK_MASTER_URL = spark://spark-master:7077
      DB_CONNECTION_STRING = ...
      INPUT_DATA_PATH=s3a://cccc/raw-data/
      OUTPUT_DATA_PATH=s3a://your-bucket/processed-data
   3. Chay tac vu theo lo
      file chinh : main_batch.py
      python src/main_batch.py
   4. Trien khai tren docker
      docker build -t your_registry/btl_bigdata_batch:latest .
      docker push your_registry/btl_bigdata_batch:latest
   5. Trien khai k8s
      # Sử dụng kubectl để tạo Job/CronJob
      kubectl apply -f ../k8s/batch-deployment.yaml



