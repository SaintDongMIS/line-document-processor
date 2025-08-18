# LINE 文件處理系統

這是一個基於 Google Cloud Platform (GCP) 的統一文件處理系統，能夠從 LINE 接收文件、使用 Document AI 進行智慧分析，並將結果存入資料庫。

## 🎯 專案目標與規劃

### 已完成功能 ✅

- **本地端 LINE Webhook 接收器**：成功實作圖片下載功能
- **Cloud Function 部署**：成功部署到 GCP Cloud Functions
- **Cloud Storage 整合**：自動將檔案上傳到 Google Cloud Storage
- **智慧檔案分類**：根據檔案類型自動分類儲存（line-images/、line-documents/、line-spreadsheets/ 等）
- **混合模式支援**：同時支援本地開發和 GCP 部署
- **圖片處理**：支援 jpg、png、gif 等格式
- **文件處理**：支援 PDF、Word、Excel 等格式
- **即時回覆**：自動回報下載狀態給用戶
- **檔案管理**：自動命名並儲存到本地桌面或雲端
- **程式碼優化**：移除無用的用戶和群組 ID 設定，簡化環境變數
- **部署腳本修復**：修復 Webhook URL 取得問題，完善部署流程

### 下一步規劃 🚀

1. **Document AI 整合**：加入文件內容分析功能
2. **資料庫儲存**：將處理結果存入 Cloud SQL
3. **完整通知系統**：透過 LINE 回傳處理結果
4. **檔案處理觸發器**：Cloud Storage 事件觸發文件處理

### 技術架構演進

```
階段 1: 本地開發 ✅
LINE Webhook → Flask Server → 本地檔案儲存

階段 2: Cloud Function + Cloud Storage ✅
LINE Webhook → Cloud Function → Cloud Storage (智慧分類)

階段 3: 完整系統 (規劃中)
LINE Webhook → Cloud Function → Cloud Storage → Document AI → Cloud SQL → LINE 通知
```

## 專案架構

### 當前架構 (階段 2 - Cloud Function + Cloud Storage)

```
line-document-processor/
├── .gitignore                 # Git 忽略檔案
├── .env.local                 # 本地環境變數 (已加入 .gitignore)
├── env.example                # 環境變數範本檔
├── requirements.txt           # 專案依賴檔
├── README.md                  # 專案說明文件
├── deploy_webhook.sh          # Cloud Function 部署腳本 (已修復)
│
├── webhook_receiver/          # Cloud Function #1: LINE Webhook 接收器 ✅
│   ├── main.py               # Cloud Function 入口點 (支援混合模式，已優化)
│   ├── requirements.txt      # Cloud Function 依賴
│   ├── .env.yaml            # Cloud Function 環境變數 (已加入 .gitignore)
│   └── env.yaml.example     # 環境變數範本 (已簡化)
│
├── document_processor/        # Cloud Function #2: 文件處理器 (預留)
│   └── main.py               # Document AI 處理主程式
│
├── scripts/                   # 部署和設定腳本
│   ├── setup_env.py          # 環境變數管理工具 (已優化)
│   └── manage.sh             # 部署管理腳本
│
└── local_test/               # 本地測試工具
    ├── test_webhook.py       # LINE Webhook 測試腳本
    └── sample_event.json     # 測試事件模擬資料
```

### 目標架構 (階段 3 - 完整系統)

```
line-document-processor/
├── webhook_receiver/          # Cloud Function #1: LINE Webhook 接收器 ✅
│   ├── main.py               # Cloud Function 入口點
│   ├── requirements.txt      # Cloud Function 依賴
│   ├── .env.yaml            # Cloud Function 環境變數
│   └── .env.yaml.example    # 環境變數範本
│
├── document_processor/        # Cloud Function #2: 文件處理器 (開發中)
│   ├── main.py               # Document AI 處理主程式
│   ├── requirements.txt      # Cloud Function 依賴
│   ├── .env.yaml            # Cloud Function 環境變數
│   └── .env.yaml.example    # 環境變數範本
│
└── local_test/               # 本地測試工具 (保留)
```

## 功能特色

- **LINE 整合**: 自動接收 LINE 用戶上傳的文件
- **智慧檔案分類**: 根據檔案類型自動分類儲存
  - `line-images/`: 圖片檔案 (jpg, png, gif, bmp, webp)
  - `line-documents/`: 文件檔案 (pdf, doc, docx, txt, rtf)
  - `line-spreadsheets/`: 試算表檔案 (xls, xlsx, csv)
  - `line-presentations/`: 簡報檔案 (ppt, pptx)
  - `line-archives/`: 壓縮檔案 (zip, rar, 7z)
  - `line-others/`: 其他類型檔案
- **混合模式**: 同時支援本地開發和 GCP 部署
- **Document AI 處理**: 使用 Google Document AI 進行智慧文件分析 (規劃中)
- **雲端儲存**: 自動將文件上傳至 Google Cloud Storage
- **結構化輸出**: 將分析結果轉換為 CSV 和 JSON 格式 (規劃中)
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
cp .env.example .env.local

# 編輯 .env.local 檔案，填入您的設定
```

#### 必要的環境變數：

```bash
# LINE Bot 設定
LINE_CHANNEL_ACCESS_TOKEN="your-line-channel-access-token"
LINE_CHANNEL_SECRET="your-line-channel-secret"
LINE_CHANNEL_ID="your-line-channel-id"

# Cloud Storage 設定 (Cloud Function 使用)
BUCKET_NAME="line-document-processor-your-project-id"

# Webhook URL (本地開發時使用 ngrok)
WEBHOOK_URL="https://your-ngrok-url.ngrok.io"

# 應用程式設定
DEBUG="True"
LOG_LEVEL="INFO"
ENVIRONMENT="local"
```

**注意**：已移除不必要的用戶和群組 ID 設定，程式會自動從 LINE Webhook 事件中取得用戶資訊。

### 3. GCP 本地驗證

```bash
# 安裝 gcloud CLI 並登入
gcloud auth application-default login

# 設定 GCP 專案
gcloud config set project YOUR_PROJECT_ID
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

### 階段 2: Cloud Function 部署 (已完成)

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
# 使用環境變數管理工具 (推薦)
python scripts/setup_env.py setup

# 或手動複製環境變數範本
cp webhook_receiver/env.yaml.example webhook_receiver/.env.yaml
# 編輯 .env.yaml 填入您的 LINE Bot 設定
```

#### 3. 部署 Webhook 接收器

```bash
# 使用部署腳本 (推薦)
./deploy_webhook.sh

# 或手動部署
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
gcloud functions describe line-webhook-receiver --region=asia-east1 --format="value(url)"

# 將此 URL 設定到 LINE Developers Console 的 Webhook URL
# 範例：https://asia-east1-annular-welder-684.cloudfunctions.net/line-webhook-receiver
```

### 階段 3: Document AI 整合 (規劃中)

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

- 自動觸發：當檔案上傳到 GCS 時自動執行 (規劃中)

## 資料流程

1. **LINE 用戶上傳文件** → LINE Bot 接收 ✅
2. **Webhook 接收器** → 下載文件並上傳到 GCS ✅
3. **智慧檔案分類** → 根據檔案類型分類儲存 ✅
4. **GCS 觸發器** → 自動啟動文件處理器 (規劃中)
5. **Document AI** → 分析文件內容 (規劃中)
6. **結果儲存** → 將結構化資料儲存到處理後的 bucket (規劃中)
7. **LINE 通知** → 回傳處理結果給用戶 (規劃中)

## 支援的檔案格式

### 圖片檔案

- PNG, JPEG/JPG, GIF, BMP, WebP

### 文件檔案

- PDF, DOC, DOCX, TXT, RTF

### 試算表檔案

- XLS, XLSX, CSV

### 簡報檔案

- PPT, PPTX

### 壓縮檔案

- ZIP, RAR, 7Z

### 其他檔案

- 所有其他類型檔案

## 故障排除

### 常見問題

1. **GCP 認證錯誤**

   - 確保已執行 `gcloud auth application-default login`
   - 檢查專案 ID 是否正確

2. **LINE Webhook 無法接收**

   - 確認 LINE Channel Access Token 是否正確
   - 檢查 Webhook URL 是否可公開存取

3. **Cloud Storage 上傳失敗**

   - 確認 BUCKET_NAME 是否正確
   - 檢查 Cloud Function 權限設定

4. **檔案分類不正確**

   - 檢查檔案副檔名是否支援
   - 確認 `get_file_type()` 函數邏輯

5. **部署腳本 Webhook URL 取得失敗**

   - 確認使用正確的區域參數：`--region=asia-east1`
   - 使用正確的格式參數：`--format="value(url)"`

6. **環境變數設定問題**

   - 使用 `python scripts/setup_env.py validate` 驗證設定
   - 確認 `.env.yaml` 檔案格式正確

### 日誌查看

```bash
# 查看 Cloud Functions 日誌
gcloud functions logs read line-webhook-receiver

# 查看即時日誌 (本地開發)
tail -f webhook_receiver/main.py
```

### 健康檢查

```bash
# 測試 Cloud Function 健康狀態
curl -X GET "https://asia-east1-YOUR_PROJECT_ID.cloudfunctions.net/line-webhook-receiver"

# 預期回應
{
  "service": "line-webhook-receiver",
  "status": "healthy"
}
```

## 開發工具

### 本地測試

```bash
# 啟動 ngrok 隧道
ngrok http 8080

# 更新 Webhook URL
sed -i '' 's|WEBHOOK_URL=.*|WEBHOOK_URL="https://your-ngrok-url.ngrok.io"|' .env.local

# 驗證環境變數設定
python scripts/setup_env.py validate
```

### GCP 配置管理

```bash
# 查看當前配置
gcloud config configurations list

# 切換配置
gcloud config configurations activate CONFIG_NAME
```

## 貢獻

歡迎提交 Issue 和 Pull Request！

## 授權

MIT License
