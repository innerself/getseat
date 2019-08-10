from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import render

from getseat.models import SeatsStatusSnapshot


def index(request):
    return render(request, 'getseat/index.html')


def just_json(request):
    snapshots = SeatsStatusSnapshot.objects.all()

    data = serializers.serialize('json', snapshots)

    return HttpResponse(data, content_type='application/json')
