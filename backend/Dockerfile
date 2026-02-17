FROM python:3.11-slim

WORKDIR /app

# Create writable /tmp for SQLite database
RUN mkdir -p /tmp && chmod 1777 /tmp

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
