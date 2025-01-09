FROM python:3.9.21-alpine3.21

RUN apk add --no-cache gcc musl-dev g++ libffi-dev


RUN mkdir "/repo"

COPY ./requirements.txt /repo
COPY ./run.py /repo
COPY ./app /repo/app


WORKDIR /repo

RUN python3 -m pip install --upgrade pip
RUN pip3 install -r requirements.txt



ENV BDHOST=localhost
ENV DBNAME=jamify
ENV DBUSER=admin
ENV DBPASS=admin
ENV QUEHOST=localhost
ENV QUEPORT=616162
ENV QUEUSER=admin
ENV QUEPASS=admin

CMD python3 run.py