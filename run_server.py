import sys
import os

# Add the project root to sys.path so backend/app/main.py can find backend.app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import uvicorn
from backend.app.core.config import settings

if __name__ == "__main__":
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
