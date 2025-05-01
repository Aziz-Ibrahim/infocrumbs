from django.shortcuts import render

from .services.news import get_newsapi_headlines, get_thenewsapi_headlines
from .services.music import authenticate_lastfm
from .services.finance import get_alpha_vantage_data, get_finnhub_quote
from .services.quotes import get_quote
from .services.sports import get_sportmonks_livescores
from .services.gardening import (
    get_gardening_guides,
    get_trefle_plants,
    get_permapeople_profiles,
)

def news_view(request):
    newsapi = get_newsapi_headlines()
    thenewsapi = get_thenewsapi_headlines()
    return render(request, 'crumbs/news.html', {
        'newsapi': newsapi,
        'thenewsapi': thenewsapi,
    })

def music_view(request):
    auth_url = authenticate_lastfm()
    return render(request, 'crumbs/music.html', {
        'auth_url': auth_url
    })

def finance_view(request):
    alpha_data = get_alpha_vantage_data()
    finnhub_data = get_finnhub_quote()
    return render(request, 'crumbs/finance.html', {
        'alpha': alpha_data,
        'finnhub': finnhub_data,
    })

def quotes_view(request):
    quote = get_quote()
    return render(request, 'crumbs/quotes.html', {
        'quote': quote
    })

def sports_view(request):
    livescores = get_sportmonks_livescores()
    return render(request, 'crumbs/sports.html', {
        'livescores': livescores
    })

def gardening_view(request):
    care_guides = get_gardening_guides()
    plants = get_trefle_plants()
    profiles = get_permapeople_profiles()
    return render(request, 'crumbs/gardening.html', {
        'care_guides': care_guides,
        'plants': plants,
        'profiles': profiles,
    })
