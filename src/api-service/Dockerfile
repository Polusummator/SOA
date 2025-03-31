FROM python:3.12-alpine

WORKDIR /api-service

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./

CMD ["python", "./api_service.py"]
