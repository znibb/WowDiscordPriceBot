FROM python:3.8-slim-buster

RUN adduser pricebot

RUN mkdir -p /pricebot/data /pricebot/cogs

WORKDIR /pricebot

COPY ./requirements.txt .
RUN pip3 install -r requirements.txt

COPY bot.py .env ./
COPY ./cogs/setup.py ./cogs/usage.py ./cogs/
COPY ./data/enchanting.json ./data/

RUN chown -R pricebot:pricebot .
USER pricebot

CMD python3 bot.py
