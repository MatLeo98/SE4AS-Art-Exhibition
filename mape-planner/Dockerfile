FROM python:3.11
WORKDIR /app
COPY . .
RUN pip3 install fastapi
RUN pip install uvicorn
RUN pip install requests
CMD ["python3", "main.py"]
