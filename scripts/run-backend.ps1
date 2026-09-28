$env:PYTHONPATH = (Resolve-Path "apps/backend").Path
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
