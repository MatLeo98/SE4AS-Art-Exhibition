FROM python:3.11
WORKDIR /app
COPY . .
RUN pip3 install influxdb-client
RUN pip3 install fastapi
RUN pip3 install paho-mqtt
RUN pip3 install uvicorn
CMD ["python3", "main.py"]