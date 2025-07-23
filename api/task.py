from django_rq import job
from docling.document_converter import DocumentConverter

@job # Este decorador registra a função como uma tarefa do RQ
def teste(source):
    converter = DocumentConverter()
    result = converter.convert(source)
    return result.document.export_to_markdown() # output: "## Docling Technical Report[...]"