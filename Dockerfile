FROM python:3.8-alpine

RUN adduser -D pricebot

RUN mkdir -p /pricebot/data
WORKDIR /pricebot

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./data/enchanting.json ./data
COPY bot.py functions.py .env .

RUN chown -R pricebot:pricebot .
USER pricebot

CMD python bot.py
