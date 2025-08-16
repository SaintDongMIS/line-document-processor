# LINE 文件處理系統

這是一個基於 Google Cloud Platform (GCP) 的統一文件處理系統，能夠從 LINE 接收文件、使用 Document AI 進行智慧分析，並將結果存入資料庫。

## 🎯 專案目標與規劃

### 已完成功能 ✅

- **本地端 LINE Webhook 接收器**：成功實作圖片下載功能
- **圖片處理**：支援 jpg、png、gif 等格式
- **即時回覆**：自動回報下載狀態給用戶
- **檔案管理**：自動命名並儲存到本地桌面

### 下一步規劃 🚀

1. **Cloud Function 部署**：將本地 webhook 部署到 GCP Cloud Functions
2. **Cloud Storage 整合**：將下載的檔案儲存到 GCS 而不是本地
3. **Document AI 處理**：加入文件內容分析功能
4. **資料庫儲存**：將處理結果存入 Cloud SQL
5. **完整通知系統**：透過 LINE 回傳處理結果

### 技術架構演進

```
階段 1: 本地開發 ✅
LINE Webhook → Flask Server → 本地檔案儲存

階段 2: Cloud Function (進行中)
LINE Webhook → Cloud Function → Cloud Storage

階段 3: 完整系統 (規劃中)
LINE Webhook → Cloud Function → Cloud Storage → Document AI → Cloud SQL → LINE 通知
```

## 專案架構

### 當前架構 (階段 1 - 本地開發)

```
line-document-processor/
├── .gitignore                 # Git 忽略檔案
├── .env.local                 # 本地環境變數 (已加入 .gitignore)
├── .env.example               # 環境變數範本檔
├── requirements.txt           # 專案依賴檔
├── README.md                  # 專案說明文件
│
├── webhook_receiver/          # LINE Webhook 接收器 (本地 Flask)
│   └── main.py               # 接收 LINE Webhook 的主程式
│
├── document_processor/        # 文件處理器 (預留)
│   └── main.py               # Document AI 處理主程式
│
└── local_test/               # 本地測試工具
    ├── test_webhook.py       # LINE Webhook 測試腳本
    └── sample_event.json     # 測試事件模擬資料
```

### 目標架構 (階段 2 - Cloud Function)

```
line-document-processor/
├── webhook_receiver/          # Cloud Function #1: LINE Webhook 接收器
│   ├── main.py               # Cloud Function 入口點
│   ├── requirements.txt      # Cloud Function 依賴
│   ├── .env.yaml            # Cloud Function 環境變數 (已加入 .gitignore)
│   └── .env.yaml.example    # 環境變數範本
│
├── document_processor/        # Cloud Function #2: 文件處理器
│   ├── main.py               # Document AI 處理主程式
│   ├── requirements.txt      # Cloud Function 依賴
│   ├── .env.yaml            # Cloud Function 環境變數 (已加入 .gitignore)
│   └── .env.yaml.example    # 環境變數範本
│
└── local_test/               # 本地測試工具 (保留)
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

### 階段 2: Cloud Function 部署準備

#### 1. GCP 專案設定

```bash
# 設定 GCP 專案
gcloud config set project YOUR_PROJECT_ID

# 啟用必要的 API
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage.googleapis.com
```

#### 2. 準備 Cloud Function 檔案

```bash
# 為 webhook_receiver 建立 Cloud Function 專用檔案
cd webhook_receiver

# 複製環境變數範本並填入實際值
cp .env.yaml.example .env.yaml
# 編輯 .env.yaml 填入您的 LINE Bot 設定
```

#### 3. 部署 Webhook 接收器

```bash
# 部署到 Cloud Functions
gcloud functions deploy line-webhook-receiver \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --source webhook_receiver \
  --entry-point line_webhook \
  --env-vars-file webhook_receiver/.env.yaml
```

#### 4. 設定 LINE Webhook URL

```bash
# 取得 Cloud Function URL
gcloud functions describe line-webhook-receiver --format="value(httpsTrigger.url)"

# 將此 URL 設定到 LINE Developers Console 的 Webhook URL
```

### 階段 3: Cloud Storage 整合 (後續)

```bash
# 建立 Cloud Storage bucket
gsutil mb gs://YOUR_BUCKET_NAME

# 部署文件處理器 (觸發器)
gcloud functions deploy document-processor \
  --runtime python311 \
  --trigger-event google.storage.object.finalize \
  --trigger-resource YOUR_BUCKET_NAME \
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
