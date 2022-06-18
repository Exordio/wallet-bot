FROM python:3.9
RUN apt update && apt install libpq-dev gcc -y && apt-get clean && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /requirements.txt
ENV PYTHONUNBUFFERED 1
RUN python -m pip install -r requirements.txt
