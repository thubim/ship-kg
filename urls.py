# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.urls import include

urlpatterns = [
    url(r'^kg_django/', include('kg_django.urls', namespace='kg_django'))
]