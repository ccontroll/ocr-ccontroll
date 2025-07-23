import uuid, json
import redis
from django_rq import job
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

# setup OCR
pipeline_options = PdfPipelineOptions()
pipeline_options.ocr_options.lang = ["pt"]
CONVERTER = DocumentConverter({
    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
})

# conexão Redis para armazenar resultados temporários
redis_conn = redis.Redis()

@job
def leitor(sources: list, callback_url: str):
    batch_id = str(uuid.uuid4())
    total = len(sources)
    # contador inicial a zero
    redis_conn.set(f"{batch_id}:count", 0)
    for s in sources:
        convert_source.delay(
            s['id'], s['link'], batch_id, callback_url, total
        )
    return {"batch_id": batch_id, "enqueued": total}

@job
def convert_source(source_id, link, batch_id, callback_url, total):
    try:
        result = CONVERTER.convert(link)
        md = result.document.export_to_markdown()
        status = True
    except Exception as e:
        md = f"Error: {e}"
        status = False

    # salva resultado no hash Redis
    redis_conn.hset(batch_id, source_id, json.dumps({
        "status": status, "result": md
    }))

    # incrementa contador; se for o último, dispara callback único
    if redis_conn.incr(f"{batch_id}:count") == total:
        # recupera todos os resultados
        raw = redis_conn.hgetall(batch_id)
        results = {
            k.decode(): json.loads(v) for k, v in raw.items()
        }
        send_callback.delay(callback_url, results)
        # limpeza
        redis_conn.delete(batch_id, f"{batch_id}:count")

@job
def send_callback(callback_url, data):
    import requests
    try:
        r = requests.post(callback_url, json=data)
        r.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to send callback: {e}")
