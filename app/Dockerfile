FROM python:3.7.7-slim
MAINTAINER "renatobanzai@gmail.com"
COPY ./ /app
WORKDIR /app
RUN pip install -r requirements.txt && python -m spacy download en
ENTRYPOINT [ "python" ]