FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

VOLUME /app/data

CMD ["uvicorn", "app.__main__:app", "--host", "0.0.0.0", "--port", "8080"]
