from django.views.generic import TemplateView

class HomePageView(TemplateView):
    template_name = 'home.html'

class ScanPageView(TemplateView):
    template_name = 'scan.html'

class HistoryView(TemplateView):
    template_name = 'history.html'