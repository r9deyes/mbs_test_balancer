FROM python:3.7

EXPOSE 8000

WORKDIR /balancer_app

COPY requirements.txt /balancer_app
RUN pip install -r requirements.txt

COPY balancer_app/app.py /balancer_app
CMD python app.py
