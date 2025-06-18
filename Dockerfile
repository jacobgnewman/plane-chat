FROM python:3-alpine
RUN apk add sqlite
WORKDIR /srv
RUN pip install --upgrade pip
RUN pip install --no-cache-dir flask requests websockets
ENV FLASK_APP=app

CMD ["python3", "app.py"]
