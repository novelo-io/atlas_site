from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count
from django.http import JsonResponse
from councilman.models import Councilman


def index(request):
    data = {
        'councilmen': Councilman.objects.all().order_by('name')
    }
    return render(request, 'index.html', data)


def detail(request, slug):

    councilman = get_object_or_404(Councilman, slug=slug)

    election_expenses = list(
        councilman.expenseselection_set.all()
        .values('kind').annotate(Sum('value')).order_by('-value__sum')
    )

    votes = councilman.vote_set.get(election_year=2016)

    data = {
        'councilman': councilman,
        'votes': votes,
        'election_expenses': election_expenses
    }
    return render(request, 'detail.html', data)


def treemap(request):
    content = [
        {"name": "Partidos", "parent": "", "size": None}
    ]
    parties = [
        {"name": f"{c['party']}", "parent": "Partidos", "size": None}
        for c in
        Councilman.objects.values('party').annotate(count=Count('party'))
    ]
    councilmen = [
        {"name": f"{c.name}", "slug": f"{c.slug}", "parent": f"{c.party}", "size": 1,
         "donations": c.donation_sum()}
        for c in Councilman.objects.all()
    ]

    content.extend(parties)
    content.extend(councilmen)

    return JsonResponse(content, safe=False)
