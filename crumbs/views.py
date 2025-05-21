from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Crumb


def crumb_list(request):
    crumbs = Crumb.objects.order_by('-published_at')
    paginator = Paginator(crumbs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'crumbs/crumbs_list.html', {'page_obj': page_obj})


def crumb_detail(request, pk):
    crumb = get_object_or_404(Crumb, pk=pk)
    return render(request, 'crumbs/crumb_detail.html', {'crumb': crumb})
