FROM python: 3.14.0

WORKDIR /app 

COPY ../api . 

RUN pip install flask 

EXPOSE 5000 

CMD ["python", "app.py"] 