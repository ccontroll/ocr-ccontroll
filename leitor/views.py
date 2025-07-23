from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from api.task import leitor

@csrf_exempt
def hello(request):

    return HttpResponse("Hello world")

@csrf_exempt
def upload(request):
    if request.method == 'POST':
        callback_url = request.POST.get('callback_url')
        files = request.POST.get['files']
        # Process the file here
        if files and callback_url:
            res = leitor.delay(files)
            return HttpResponse(f"Processamento iniciado, aguarde o retorno.")
    return HttpResponseBadRequest("Método não permitido ou dados inválidos")