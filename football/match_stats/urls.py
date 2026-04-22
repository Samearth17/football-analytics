from django.shortcuts import render
from django.urls import path
from .views import match_stats_api , home_page
from .statsengine import load_events , pre_events , stats_between


urlpatterns = [
    path('', home_page, name='home'),
    path('api/match-stats/', match_stats_api, name='match_stats_api'),
]
