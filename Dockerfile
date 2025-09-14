FROM python:3.11-slim AS build

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY --from=build /usr/local /usr/local
COPY . .

RUN adduser --disabled-password --gecos "" appuser \
    && chown -R appuser:appuser /app

ENV PORT=8000
EXPOSE $PORT

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$PORT"]
