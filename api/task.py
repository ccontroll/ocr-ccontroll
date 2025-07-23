from django_rq import job
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
)

pipeline_options = PdfPipelineOptions()
pipeline_options.ocr_options.lang = ["pt"]

CONVERTER = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(
            pipeline_options=pipeline_options,
        )
    }
)

@job
def send_callback(callback_url, data):
    import requests
    try:
        response = requests.post(callback_url, json=data)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to send callback: {e}")

@job # Este decorador registra a função como uma tarefa do RQ
def leitor(sources: list, callback_url: str = None):
    results = {}
    for source in sources:
        try:
            result = CONVERTER.convert(source['link'])
            results[source['id']] = {'status': True, 'result': result.document.export_to_markdown()}
        except Exception as e:
            results[source['id']] = {'status': False, 'result': f"Error processing {source['link']}: {str(e)}"}

        if callback_url:
            send_callback(callback_url, results)
    return "processing complete", results