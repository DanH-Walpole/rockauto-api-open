This file summarizes key points from the codebase that were used to update README.md

- FastAPI application exposing various catalog and part endpoints.
- Endpoints: makes, years, models, engines, categories, sub_categories, parts, closeouts, search, vehicle_info, part_number.
- Many endpoints support optional `search_link` so callers can omit it and still navigate.
- `start.py` runs Uvicorn for convenience.
- `tests/` contains a lightweight pytest suite using FastAPI's TestClient.
