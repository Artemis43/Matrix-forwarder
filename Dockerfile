FROM python:3.11-alpine3.20
WORKDIR /fbot
COPY . /fbot/
RUN pip install -r requirements.txt
EXPOSE 8080
CMD python main.py
