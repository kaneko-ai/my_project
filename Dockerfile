FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    python -m spacy download en_core_web_sm

EXPOSE 7860 8000

RUN chmod +x start.sh
CMD ["./start.sh"]
