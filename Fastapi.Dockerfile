FROM python:3.11-slim

WORKDIR /app

COPY fastapi-requirements.txt .
RUN pip install --no-cache-dir -r fastapi-requirements.txt

COPY . .

VOLUME /app/data

CMD ["uvicorn", "app.callback_service:app", "--host", "0.0.0.0", "--port", "8000"]
