FROM python:3.9.16

WORKDIR /app

EXPOSE 4222
EXPOSE 7379

COPY . /app

RUN pip install -r requirements.txt

CMD ["python", "-u", "outputFinalLabel.py"]
