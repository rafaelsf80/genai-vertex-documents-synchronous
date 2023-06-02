# python3.8 breaks with gradio
FROM python:3.7

RUN pip install gradio 
RUN pip install google-cloud-aiplatform==1.25.0 google-cloud-logging google-cloud-documentai==2.0.3

COPY ./gradioapp /app

WORKDIR /app

EXPOSE 7860

CMD ["python", "app.py"]