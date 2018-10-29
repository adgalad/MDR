FROM python:3.6

RUN mkdir /code

WORKDIR /code

COPY . /code
COPY ./start.sh /start.sh

RUN pip3 install -r requirements.txt
EXPOSE 8000

CMD ["/start.sh"]