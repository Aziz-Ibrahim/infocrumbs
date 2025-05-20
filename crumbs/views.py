from django.shortcuts import render, get_object_or_404
from datetime import date
from django.http import JsonResponse, Http404
from django.core.paginator import Paginator

from .models import Crumb


def crumb_list(request):
    crumbs = Crumb.objects.order_by('-published_at')
    paginator = Paginator(crumbs, 10)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'crumbs/crumbs_list.html', {'page_obj': page_obj})


def infinite_crumbs(request):
    crumbs = Crumb.objects.order_by('-published_at')
    paginator = Paginator(crumbs, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    today = date.today()
    new_crumbs = []
    old_crumbs = []

    for crumb in page_obj:
        crumb_data = {
            'id': crumb.id,
            'title': crumb.title,
            'summary': crumb.summary,
            'url': crumb.url,
            'source': crumb.source,
            'topic': crumb.topic.name,
            'published_at': crumb.published_at.strftime('%Y-%m-%d %H:%M'),
        }

        if crumb.published_at.date() == today:
            new_crumbs.append(crumb_data)
        else:
            old_crumbs.append(crumb_data)

    return JsonResponse({
        'new': new_crumbs,
        'old': old_crumbs,
        'has_next': page_obj.has_next(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
    })


def crumb_detail(request, pk):
    crumb = get_object_or_404(Crumb, pk=pk)
    return render(request, 'crumbs/crumb_detail.html', {'crumb': crumb})


def crumb_detail_api(request, pk):
    try:
        crumb = Crumb.objects.select_related('topic').get(pk=pk)
        return JsonResponse({
            'id': crumb.id,
            'title': crumb.title,
            'summary': crumb.summary,
            'url': crumb.url,
            'source': crumb.source,
            'topic': crumb.topic.name,
            'published_at': crumb.published_at,
        })
    except Crumb.DoesNotExist:
        raise Http404("Crumb not found")