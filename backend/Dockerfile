FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

ARG CACHEBUSTER=1
RUN pip install --no-cache-dir -r requirements.txt
RUN #pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "__main__.py"]
