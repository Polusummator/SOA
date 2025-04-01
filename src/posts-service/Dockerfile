FROM python:3.12-alpine

WORKDIR /posts-service

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./
RUN chmod +x ./gen_proto.sh
RUN ./gen_proto.sh

CMD ["python", "./posts_service.py"]
