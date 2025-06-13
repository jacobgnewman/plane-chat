FROM python:3-alpine
RUN apk add sqlite
WORKDIR /srv
RUN pip install --upgrade pip
RUN pip install flask requests flask-socketio
ENV FLASK_APP=app
CMD ["python", "app.py"]
