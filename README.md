# Bambu Filament Manager

A locally hosted web application to manage your 3D printing filament inventory and track usage.

## Features

- **Inventory Management:** Track your spools, remaining weight, colors, and prices.
- **G-code Parsing:** Drag and drop `.gcode` or `.3mf` files to automatically detect filament usage.
- **Print Logging:** Log successful prints to automatically deduct filament from your inventory.
- **Statistics:** View monthly usage and most used colors.
- **Visual Interface:** "Spreadsheet-style" manual entry and visual slot selection for multi-color prints.

## Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application:**
   Double-click `run_app.bat` 
   
   OR run manually:
   ```bash
   # Terminal 1 (Backend)
   uvicorn app.main:app --reload

   # Terminal 2 (Frontend)
   streamlit run dashboard.py
   ```

## Usage

1. Open the dashboard (usually http://localhost:8501).
2. Go to "Add Filament" to populate your inventory.
3. Use "Log Print" to upload a G-code file.
4. Select the spools corresponding to the slots detected in the file.
5. Click "Log Print Job".

## Technology Stack

- **Backend:** FastAPI, SQLite, SQLAlchemy
- **Frontend:** Streamlit

