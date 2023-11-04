FROM python:3.11
WORKDIR /app
COPY . .
RUN pip3 install influxdb-client
RUN pip install paho-mqtt
CMD ["python3", "main.py"]
