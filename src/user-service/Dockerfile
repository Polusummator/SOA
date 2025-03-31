FROM python:3.12-alpine

WORKDIR /user-service

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./

CMD ["python", "./user_service.py"]
