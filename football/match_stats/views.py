from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .statsengine import stats_between, load_events, pre_events

@api_view(['GET'])
def match_stats_api(request):
    try:
        start = int(float(request.GET.get('start', '0')))
        end = min(int(float(request.GET.get('end', '5400'))), 5400)
    except (ValueError, TypeError):
        start = 0
        end = 5400
    
    data = stats_between(None, start, end, None, None)  
    return Response(data)

def home_page(request):
    return render(request, 'home_page.html')
