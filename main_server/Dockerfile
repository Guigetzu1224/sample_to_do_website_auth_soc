FROM python:3

EXPOSE 5000/tcp

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

CMD [ "/app/run.sh" ]

