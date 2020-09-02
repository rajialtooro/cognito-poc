FROM python:3.7

EXPOSE 80

COPY . .

RUN pip install -r requirements.txt

CMD ["sh", "run.prod.sh"]