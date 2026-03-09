# Development: runs Vite dev server + FastAPI with hot reload
run-dev:
    #!/usr/bin/env bash
    trap 'kill 0' EXIT
    cd ui && npm run dev &
    uvicorn gmail_filter_converter.server:app --reload --port 8000 &
    wait

# Production: builds frontend, then serves everything from FastAPI
run:
    cd ui && npm run build
    uvicorn gmail_filter_converter.server:app --port 8000
