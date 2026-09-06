FROM python:3.10-slim

RUN pip install --no-cache-dir gradio
RUN pip install google-cloud-aiplatform google-genai google-cloud-logging google-cloud-documentai

COPY ./gradioapp /app

WORKDIR /app

EXPOSE 7860

CMD ["python", "app.py"]