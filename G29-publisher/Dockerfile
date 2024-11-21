FROM python:3.9-slim

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir kuksa-client pygame
CMD ["python3", "/app/src/client.py"]