FROM ubuntu:latest
LABEL authors="matth"

ENTRYPOINT ["top", "-b"]