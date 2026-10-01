# Shuttle Session Tracker

A small web application for campus shuttle booking management. This project includes a FastAPI backend and a Vue 3 frontend that consume the same in-memory dataset.

## Project overview

- Backend: FastAPI with in-memory dataset
- Frontend: Vue 3 + Vite
- Domain: campus transportation / shuttle booking
- Purpose: track shuttle sessions, search/filter records, create new ones, and delete existing ones

## Requirements covered

- Synthetic in-memory dataset with 12 rows in backend/app/data.py
- GET /sessions with pagination and search
- GET /sessions/{id} with 404 fallback
- POST /sessions with Pydantic validation and 201 Created response
- DELETE /sessions/{id} with 204 No Content response
- CORS allows the Vue frontend origin
- Frontend list state with retry support, create form validation, and delete confirmation

## Prerequisites

- Python 3.11 or newer
- Node.js 18 or newer
- npm

## Backend setup

1. Open a terminal in the project root.
2. Run:

   cd backend
   python -m pip install -r requirements.txt

3. Start the API server:

   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

The API will be available at http://localhost:8000.

## Frontend setup

1. Open a second terminal in the project root.
2. Run:

   cd frontend
   npm install
   npm run dev -- --host 0.0.0.0

3. Open the browser at:

   http://localhost:5173

## API verification

Run the following commands in a terminal while the backend is running:

### List sessions with pagination and search

curl "http://localhost:8000/sessions?page=1&limit=5&search=kampus"

### Get one session

curl http://localhost:8000/sessions/1

### Create a new session

curl -X POST "http://localhost:8000/sessions" \
  -H "Content-Type: application/json" \
  -d '{
    "route_name": "Kampus - Cibubur",
    "driver_name": "Nanda Putra",
    "departure_time": "14:00",
    "passenger_name": "Faizal Anwar",
    "destination": "Cibubur",
    "seat_count": 3,
    "status": "scheduled"
  }'

### Delete a session

curl -X DELETE http://localhost:8000/sessions/1

### Get nonexistent session

curl -i http://localhost:8000/sessions/999

Expected result: HTTP 404 with a JSON error message.

## Frontend verification

1. Open http://localhost:5173.
2. Confirm the session table loads from the backend.
3. Test the search field to filter items.
4. Add a new session with the form and verify it appears in the list.
5. Click Delete to confirm the remove flow works.
6. Try invalid form input and confirm validation is displayed.
7. Use the Retry button when the backend is unavailable to see the error state.

## Notes

- The backend stores data in memory only, so it resets when the server restarts.
- The CORS configuration is set to allow the Vue frontend at http://localhost:5173.

