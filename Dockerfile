FROM python:3.7
COPY requirements.txt .

RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY /dashboard /app/dashboard
COPY /data /app/data