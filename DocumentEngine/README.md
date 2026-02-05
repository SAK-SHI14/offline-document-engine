# Offline Document Intelligence Engine

**A Production-Grade, Privacy-First OCR & Document Analysis System**

This engine processes document images entirely offline, using a layered architecture to extract text, layout structure, tables, and entities without sending a single byte to the cloud.

---

## 🏗 Architecture

The system follows a strict 6-Layer Pipeline:

1.  **Ingestion Layer**: Validates and loads images safely.
2.  **Vision Preprocessing**: Corrects skew (rotation), removes noise, and applies adaptive thresholding to handle scanned document artifacts.
3.  **OCR Core**: Uses **Tesseract 5 LSTM** with a multi-pass strategy to extract text coordinates and structure.
4.  **Layout Engine**: Uses Computer Vision (morphological operations) to detect tables and classify text blocks (Headers vs Paragraphs).
5.  **Post-Processing**: Regex-based NLP to extract entities (Dates, Emails, Amounts) and normalize text.
6.  **Serialization**: Exports data into a strict, versioned JSON schema using **Pydantic**.

## 🚀 Quick Start

### Prerequisites
1.  **Python 3.10+**
2.  **Tesseract OCR** must be installed on your system.
    -   Windows: [Download Installer](https://github.com/UB-Mannheim/tesseract/wiki)
    -   Ensure `tesseract.exe` is in your PATH or update `.env`.

### Installation

```bash
# 1. Install Dependencies
pip install -r requirements.txt

# 2. Check Configuration
# Edit app/core/config.py if your Tesseract path is custom
```

### Running the System

You need two terminals (or run as background processes):

**Terminal 1: The Backend API**
```bash
# From inside DocumentEngine directory
uvicorn app.main:app --reload
```

**Terminal 2: The Frontend UI**
```bash
streamlit run ui/dashboard.py
```

---

## 🔌 API Usage

**POST** `/api/v1/process`
-   **Input**: `multipart/form-data` (file)
-   **Output**: JSON Document

**Example Output Structure:**
```json
{
  "document_id": "...",
  "text_content": { "full_text": "..." },
  "layout": { "blocks": [ ... ] },
  "tables": [ ... ],
  "entities": { ... },
  "processing_metadata": { "processed_offline": true }
}
```

## 🛠 Tuning & Customization

-   **Skew Correction**: In `app/services/preprocessing.py`. Adjust the angle threshold in `correct_skew`.
-   **Table Detection**: In `app/services/layout_engine.py`. Adjust the `kernel` size (`(25, 1)`) to detect shorter or longer lines.
-   **OCR Config**: In `app/services/ocr_service.py`. Modify `psm` (Page Segmentation Mode) if your documents are complex (e.g., specific columns).

## 🔒 Security & Privacy

-   **Zero External Calls**: The codebase contains NO network calls to external APIs.
-   **Local Processing**: All memory operations happen within the Python process.
-   **No Persistence**: Uploaded files are processed in-memory (using `tempfile` SpooledTemporaryFile via FastAPI) and discarded.
