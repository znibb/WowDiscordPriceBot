FROM python:3.8-slim-buster

RUN adduser pricebot

RUN mkdir -p /pricebot/data
WORKDIR /pricebot

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

COPY ./data/enchanting.json ./data
COPY bot.py functions.py .env ./

RUN chown -R pricebot:pricebot .
USER pricebot

CMD python3 bot.py
