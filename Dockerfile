#FROM python:3.9
#
#WORKDIR /app
#
#COPY requirements.txt requirements.txt
#
#RUN pip3 install -r requirements.txt
#
#COPY . .
#
#CMD ["python3","manage.py","runserver","0.0.0.0:8000"]


FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/

CMD ["python3","manage.py","makemigrations"]
CMD ["python3","manage.py","migrate"]
CMD ["python3","manage.py","test"]
CMD ["python3","manage.py","runserver","0.0.0.0:8000"]