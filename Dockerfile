FROM python:3.12-slim
ARG APP_VERSION=4.0.0
ENV APP_VERSION=${APP_VERSION}
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app/ ./app/
ENV PYTHONPATH=/app
EXPOSE 5000
CMD ["python3", "app/app.py"]
