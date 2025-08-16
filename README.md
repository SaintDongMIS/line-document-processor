# LINE 文件處理系統

這是一個基於 Google Cloud Platform (GCP) 的統一文件處理系統，能夠從 LINE 接收文件、使用 Document AI 進行智慧分析，並將結果存入資料庫。

## 專案架構

```
line-document-processor/
├── .gitignore                 # Git 忽略檔案
├── env.example                # 環境變數範本檔
├── requirements.txt           # 專案依賴檔
├── README.md                  # 專案說明文件
│
├── webhook_receiver/          # LINE Webhook 接收器
│   └── main.py               # 接收 LINE Webhook 的主程式
│
├── document_processor/        # 文件處理器
│   └── main.py               # Document AI 處理主程式
│
└── local_test/               # 本地測試工具
    ├── test_webhook.py       # LINE Webhook 測試腳本
    └── sample_event.json     # GCS 觸發事件模擬資料
```

## 功能特色

- **LINE 整合**: 自動接收 LINE 用戶上傳的文件
- **Document AI 處理**: 使用 Google Document AI 進行智慧文件分析
- **雲端儲存**: 自動將文件上傳至 Google Cloud Storage
- **結構化輸出**: 將分析結果轉換為 CSV 和 JSON 格式
- **本地開發支援**: 完整的本地測試環境

## 安裝與設定

### 1. 建立 Python 虛擬環境

```bash
# 建立虛擬環境
python -m venv venv

# 啟用虛擬環境 (Mac/Linux)
source venv/bin/activate

# 啟用虛擬環境 (Windows)
.\venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt
```

### 2. 設定環境變數

```bash
# 複製環境變數範本
cp env.example .env

# 編輯 .env 檔案，填入您的設定
```

#### 必要的環境變數：

```bash
# GCP 專案設定
GCP_PROJECT="your-gcp-project-id"
BUCKET_NAME="raw-invoices"
PROCESSED_BUCKET_NAME="processed-data"
DOCAI_LOCATION="us"
DOCAI_PROCESSOR_ID="your-processor-id"

# LINE Bot 設定
LINE_CHANNEL_ACCESS_TOKEN="your-line-channel-access-token"
LINE_CHANNEL_SECRET="your-line-channel-secret"
```

### 3. GCP 本地驗證

```bash
# 安裝 gcloud CLI 並登入
gcloud auth application-default login
```

## 本地開發與測試

### 測試 LINE Webhook 接收器

```bash
# 啟動本地測試伺服器
python webhook_receiver/main.py

# 在另一個終端視窗中執行測試
python local_test/test_webhook.py
```

### 測試文件處理器

```bash
# 直接執行本地測試
python document_processor/main.py
```

## 部署到 GCP

### 1. 部署 Webhook 接收器

```bash
# 部署到 Cloud Functions
gcloud functions deploy line-webhook-receiver \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated \
  --source webhook_receiver \
  --entry-point line_webhook
```

### 2. 部署文件處理器

```bash
# 部署到 Cloud Functions (觸發器)
gcloud functions deploy document-processor \
  --runtime python39 \
  --trigger-event google.storage.object.finalize \
  --trigger-resource raw-invoices \
  --source document_processor \
  --entry-point process_document
```

## API 端點

### Webhook 接收器

- `POST /`: 接收 LINE Webhook 事件
- `GET /health`: 健康檢查端點

### 文件處理器

- 自動觸發：當檔案上傳到 GCS 時自動執行

## 資料流程

1. **LINE 用戶上傳文件** → LINE Bot 接收
2. **Webhook 接收器** → 下載文件並上傳到 GCS
3. **GCS 觸發器** → 自動啟動文件處理器
4. **Document AI** → 分析文件內容
5. **結果儲存** → 將結構化資料儲存到處理後的 bucket

## 支援的檔案格式

- PDF
- PNG
- JPEG/JPG
- TIFF
- GIF

## 故障排除

### 常見問題

1. **GCP 認證錯誤**

   - 確保已執行 `gcloud auth application-default login`
   - 檢查專案 ID 是否正確

2. **LINE Webhook 無法接收**

   - 確認 LINE Channel Access Token 是否正確
   - 檢查 Webhook URL 是否可公開存取

3. **Document AI 處理失敗**
   - 確認 Processor ID 是否正確
   - 檢查檔案格式是否支援

### 日誌查看

```bash
# 查看 Cloud Functions 日誌
gcloud functions logs read line-webhook-receiver
gcloud functions logs read document-processor
```

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 授權

MIT License
