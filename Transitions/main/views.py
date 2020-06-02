from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
# Create your views here.


class MainView(TemplateView):
    template_name = 'index.html'

    def post(self, request):
        print(request.body)
        return render(request, 'index.html')


class TestView(TemplateView):
    def get(self, request):
        return JsonResponse({'message': 'Hello from the other side'})
