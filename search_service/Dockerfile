# 1. Παίρνουμε μια έτοιμη, ελαφριά έκδοση της Python
FROM python:3.11-slim

# 2. Φτιάχνουμε έναν φάκελο εργασίας μέσα στο container
WORKDIR /app

# 3. Αντιγράφουμε ΠΡΩΤΑ το requirements.txt (για να εκμεταλλευτούμε την cache του Docker)
COPY requirements.txt .

# 4. Εγκαθιστούμε τις βιβλιοθήκες (FastAPI, requests, uvicorn κλπ.)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Αντιγράφουμε τον υπόλοιπο κώδικά μας (main.py, schemas.py)
COPY . .

# 7. Η εντολή που θα τρέχει αυτόματα όταν σηκώνεται το container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8086"]
