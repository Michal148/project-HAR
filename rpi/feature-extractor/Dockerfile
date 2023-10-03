FROM python:3.9.16

WORKDIR /app

EXPOSE 4222

COPY . /app

RUN pip install -r requirements.txt
CMD ["python", "FeatureExtractor.py"]
