from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1 as documentai

import vertexai
from vertexai.preview.language_models import TextGenerationModel

import google.cloud.logging

import gradio as gr

PROJECT_ID = "argolis-rafaelsanchez-ml-dev"
REGION = "us-central1" 

client = google.cloud.logging.Client(project=PROJECT_ID)
client.setup_logging()

log_name = "genai-vertex-unstructured-log"
logger = client.logger(log_name)


def ocr_parser(file):

    FILE_PATH = file.name # Getting filename, since file type is tempfile._TemporaryFileWrapper
    MIME_TYPE = "application/pdf"

    PROJECT_ID = "argolis-rafaelsanchez-ml-dev"
    LOCATION = "eu"
    PROCESSOR_ID = "a99d341e2c8c2e1c" # ocr processor

    # Instantiates a client
    docai_client = documentai.DocumentProcessorServiceClient(
        client_options=ClientOptions(api_endpoint=f"{LOCATION}-documentai.googleapis.com")
    )

    RESOURCE_NAME = docai_client.processor_path(PROJECT_ID, LOCATION, PROCESSOR_ID)

    # Read the file into memory
    with open(FILE_PATH, "rb") as image:
        image_content = image.read()

    # Load Binary Data into Document AI RawDocument Object
    raw_document = documentai.RawDocument(content=image_content, mime_type=MIME_TYPE)

    # Configure the process request
    request = documentai.ProcessRequest(name=RESOURCE_NAME, raw_document=raw_document)

    # Use the Document AI client to process the sample form
    result = docai_client.process_document(request=request)

    document_object = result.document
    logger.log_text("Document processing complete.")
    logger.log_text(f"Text: {document_object.text}")
    return document_object.text

def llm_insights(prompt, ocr, include_ocr):
    
    vertexai.init(project=PROJECT_ID, location=REGION)

    model = TextGenerationModel.from_pretrained("text-bison@001") 

    if ocr == "" or prompt == "":
        return "ERROR: No files selected or prompt empty. Upload a file first"

    logger.log_text("Sending to predict")

    total_prompt = f"""
        Answer the question based on the context below. Extract the exact full sentence that contains the answer. If the question cannot be answered using the information provided answer with “I cannot find the data”

        Context: {ocr} 

        Question: {prompt}

        Answer:
    """

    logger.log_text(total_prompt)

    answer = model.predict(
        total_prompt,#prompt+" "+ocr if include_ocr else prompt,
        max_output_tokens=256,
        temperature=0.2,
        top_p=0.8,
        top_k=40)

    return answer

demo = gr.Blocks()

with demo:
    gr.Markdown("# DOCUMENT SEMANTIC SEARCH DEMO SEMI-STRUCTURED (MAX_PAGES 15)")

    docai_file = gr.File(label="Upload doc. Max pages: 15", type="file")
    
    gr.Markdown("### PROMPT: Ask questions on the doc with the checkbutton enabled. Example: 'How much is the trip cost?', 'What is the name of the traveller'")
    prompt = gr.Textbox(label="Prompt")
    include_ocr_prompt = gr.Checkbox(label="Include OCR in prompt", value=True)
    
    b = gr.Button("Submit", variant="primary")
    
    answer = gr.Textbox(label="Output", variant="secondary")
    ocr = gr.Textbox(label="Show OCR. Debugging purposes. Read-only field", max_lines=20)
    docai_file.change(ocr_parser, inputs=docai_file, outputs=ocr)

    b.click(llm_insights, inputs=[prompt,ocr,include_ocr_prompt], outputs=answer)

demo.launch(server_name="0.0.0.0", server_port=7860)

