FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
 
RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app

ENV PORT=8000
EXPOSE $PORT

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]

