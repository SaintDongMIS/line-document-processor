import os
import json
import pandas as pd
from datetime import datetime
from google.cloud import documentai_v1 as documentai
from google.cloud import storage
from dotenv import load_dotenv

# --- 初始化 ---
if os.environ.get('FUNCTIONS_FRAMEWORK') is None:
    load_dotenv()

# --- 從環境變數讀取設定 ---
PROJECT_ID = os.environ.get('GCP_PROJECT')
LOCATION = os.environ.get('DOCAI_LOCATION')
PROCESSOR_ID = os.environ.get('DOCAI_PROCESSOR_ID')
PROCESSED_BUCKET_NAME = os.environ.get('PROCESSED_BUCKET_NAME')

# 初始化 GCP 客戶端
docai_client = documentai.DocumentProcessorServiceClient()
storage_client = storage.Client()

def process_document(event, context):
    """GCS 觸發的背景函式 (GCP上的進入點)"""
    try:
        bucket_name = event['bucket']
        file_name = event['name']
        
        print(f"開始處理來自 {bucket_name} 的檔案: {file_name}")
        
        # 處理文件
        result = process_with_documentai(bucket_name, file_name)
        
        # 儲存結果
        save_results(file_name, result)
        
        print(f"檔案 {file_name} 處理完成")
        
    except Exception as e:
        print(f"處理文件時發生錯誤: {e}")
        raise

def process_with_documentai(bucket_name, file_name):
    """使用 Document AI 處理文件"""
    gcs_uri = f"gs://{bucket_name}/{file_name}"
    
    # 根據檔案副檔名判斷 MIME 類型
    mime_type = get_mime_type(file_name)
    print(f"使用 MIME 類型: {mime_type}")

    # 建立 Document AI 請求
    gcs_document = documentai.GcsDocument(gcs_uri=gcs_uri, mime_type=mime_type)
    request_payload = documentai.ProcessRequest(
        name=docai_client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID),
        gcs_document=gcs_document
    )
    
    # 呼叫 Document AI
    print("呼叫 Document AI...")
    result = docai_client.process_document(request=request_payload)
    document = result.document
    
    print(f"Document AI 處理完成，頁數: {len(document.pages)}")
    
    return document

def get_mime_type(file_name):
    """根據檔案副檔名判斷 MIME 類型"""
    file_extension = file_name.lower().split('.')[-1]
    
    mime_types = {
        'pdf': 'application/pdf',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'tiff': 'image/tiff',
        'gif': 'image/gif'
    }
    
    return mime_types.get(file_extension, 'application/pdf')

def save_results(file_name, document):
    """儲存處理結果"""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    
    # 1. 儲存原始 JSON 結果
    json_blob_name = f"{timestamp}_{file_name}.json"
    json_blob = storage_client.bucket(PROCESSED_BUCKET_NAME).blob(json_blob_name)
    json_blob.upload_from_string(
        documentai.Document.to_json(document),
        content_type='application/json'
    )
    print(f"JSON 結果已儲存: {json_blob_name}")
    
    # 2. 解析並儲存結構化資料
    extracted_data = extract_structured_data(document)
    if extracted_data:
        csv_blob_name = f"{timestamp}_{file_name}.csv"
        csv_blob = storage_client.bucket(PROCESSED_BUCKET_NAME).blob(csv_blob_name)
        
        df = pd.DataFrame(extracted_data)
        csv_blob.upload_from_string(
            df.to_csv(index=False, encoding='utf-8'),
            content_type='text/csv'
        )
        print(f"CSV 結果已儲存: {csv_blob_name}")
        print("擷取的資料:")
        print(df)

def extract_structured_data(document):
    """從 Document AI 結果中提取結構化資料"""
    extracted_data = []
    
    # 提取實體 (Entities)
    for entity in document.entities:
        data = {
            'type': entity.type_,
            'value': entity.mention_text,
            'confidence': entity.confidence,
            'page': entity.page_anchor.page_refs[0].page if entity.page_anchor.page_refs else None
        }
        extracted_data.append(data)
    
    # 提取表格 (Tables)
    for page in document.pages:
        for table in page.tables:
            for row in table.header_rows:
                for cell in row.cells:
                    data = {
                        'type': 'table_header',
                        'value': cell.text,
                        'confidence': 1.0,
                        'page': page.page_number
                    }
                    extracted_data.append(data)
            
            for row in table.body_rows:
                for cell in row.cells:
                    data = {
                        'type': 'table_body',
                        'value': cell.text,
                        'confidence': 1.0,
                        'page': page.page_number
                    }
                    extracted_data.append(data)
    
    return extracted_data

def local_trigger():
    """本地測試用的函式"""
    print("開始本地測試...")
    
    # 讀取 local_test/sample_event.json 來模擬觸發事件
    try:
        with open('local_test/sample_event.json', 'r', encoding='utf-8') as f:
            mock_event = json.load(f)
        
        process_document(mock_event, None)
        print("本地測試完成")
        
    except FileNotFoundError:
        print("找不到 sample_event.json 檔案，請先建立測試資料")
        print("範例格式:")
        print('''
{
    "bucket": "your-bucket-name",
    "name": "test-document.pdf"
}
        ''')

if __name__ == "__main__":
    # 讓您可以在本地端直接執行 `python document_processor/main.py` 來測試此函式
    local_trigger()
