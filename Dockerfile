FROM python:3.9.21-bookworm

#RUN apt install gcc musl-dev g++ libffi-dev


RUN mkdir "/repo"

COPY ./requirements.txt /repo
COPY ./run.py /repo
COPY ./app /repo/app
COPY ./models /repo/models


WORKDIR /repo

RUN python3 -m pip install --upgrade pip
RUN pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
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