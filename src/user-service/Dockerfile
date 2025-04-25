FROM python:3.12-slim

WORKDIR /user-service

RUN apt-get update && \
    apt-get install -y librdkafka-dev gcc libpq-dev

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./

CMD ["python", "./user_service.py"]
