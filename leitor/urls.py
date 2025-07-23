from django.urls import path
from leitor import views

urlpatterns = [
    path('hello/', views.hello, name='hello'),
    path('upload/', views.upload, name='upload'),
]