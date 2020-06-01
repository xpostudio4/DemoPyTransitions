from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.


class MainView(TemplateView):
    template_name = 'index.html'

    def post(self, request):
        print('From post request')
        return render(request, 'index.html')
