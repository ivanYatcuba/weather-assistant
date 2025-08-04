FROM python:3.12

WORKDIR /app

COPY . /app

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

RUN export PYTHONPATH=/app:$PYTHONPATH

ENV GEOAPIFYKEY key

CMD ["sh", "-c", "export PYTHONPATH=/app:$PYTHONPATH && python /app/mcp-server.py"]