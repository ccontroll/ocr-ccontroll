from api.task import leitor

class OCR:
    def __init__(self, arquivo, callback):
        self.name = "OCR Processor"
    
    def ler(self, data):
        # Process the OCR data
        return f"Processed data: {data}"