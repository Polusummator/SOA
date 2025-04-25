FROM python:3.12-slim

WORKDIR /posts-service

RUN apt-get update && \
    apt-get install -y librdkafka-dev gcc libpq-dev

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./
RUN chmod +x ./gen_proto.sh
RUN ./gen_proto.sh

CMD ["python", "./posts_service.py"]
