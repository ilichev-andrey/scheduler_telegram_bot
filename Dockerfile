FROM python:3.9.2

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt-get update && \
    apt-get install -y locales git && \
    sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    pip install -U pip && \
    python -m pip install git+https://github.com/ilichev-andrey/scheduler_core.git && \
    python -m pip install git+https://github.com/ilichev-andrey/python-telegram-bot-calendar.git && \
    pip install --no-cache-dir -r requirements.txt

ENV TZ=Europe/Moscow \
    LANG=ru_RU.UTF-8 \
    LANGUAGE=ru_RU \
    LC_ALL=ru_RU.UTF-8
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

COPY . .