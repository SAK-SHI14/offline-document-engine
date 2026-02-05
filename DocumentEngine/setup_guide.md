# Setup Guide: Offline OCR Engine

## 1. Install Tesseract OCR (Critical Step)
Since existing Python OCR libraries are wrappers, you **must** have the binary engine installed.

### Windows
1.  Download the **Tesseract UB Mannheim Installer**:  
    [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
2.  Run the installer.
3.  **IMPORTANT**: Note the installation path. Default is usually:
    `C:\Program Files\Tesseract-OCR`
4.  **Add to PATH**:
    -   Search "Edit the system environment variables" in Windows.
    -   Click "Environment Variables".
    -   Under "System variables", find `Path` -> Edit -> New.
    -   Paste `C:\Program Files\Tesseract-OCR`.
5.  **Verify**:
    Open a NEW terminal (PowerShell) and type:
    ```powershell
    tesseract --version
    ```
    If you see version output (e.g., `tesseract v5.x.x`), you are good.

## 2. Python Environment

It is recommended to use a virtual environment.

```powershell
# Create venv
python -m venv venv

# Activate venv
.\venv\Scripts\Activate.ps1

# Install project deps
pip install -r requirements.txt
```

## 3. Verify Configuration

Open `app/core/config.py` and check these lines:

```python
TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
```

If you installed Tesseract elsewhere, you can either:
1.  Edit this file directly.
2.  OR Set an environment variable: `$env:TESSERACT_CMD="D:\MyApps\Tesseract\tesseract.exe"`

## 4. Run the App

```powershell
uvicorn app.main:app --reload
```
Go to `http://localhost:8000/docs` to test the API directly via Swagger UI.
