from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def index(request):
    return render(request, 'papers/index.html')


def detail(request):
    key_word = request.POST['kw']

    return render(request, 'papers/detail.html', {'key_word':key_word})
