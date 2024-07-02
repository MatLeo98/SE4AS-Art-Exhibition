FROM python:3.11
WORKDIR /app
COPY . .
RUN pip3 install influxdb-client
RUN pip3 install numpy
RUN pip3 install requests
CMD ["python3", "main.py"]