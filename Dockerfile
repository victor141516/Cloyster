FROM python:3-alpine

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN pip install gunicorn
CMD [ "gunicorn", "-w4", "-b", ":8000", "main:app" ]
