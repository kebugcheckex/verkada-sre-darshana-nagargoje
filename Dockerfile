FROM python:3.12
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r /app/requirements.txt
COPY run.sh /app/
RUN chmod 755 /app/run.sh
CMD /app/run.sh
