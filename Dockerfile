FROM python:3.9.2

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt-get update && \
    apt-get install -y git && \
    pip install -U pip && \
    python -m pip install git+https://github.com/ilichev-andrey/scheduler_core.git && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]