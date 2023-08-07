"""kg_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf.urls import url
from . import view

from . import settings
from django.conf.urls.static import static

app_name = 'kg_django'
urlpatterns = [
    url(r'^testnear', view.find_near_before),
    url(r'^is_friends', view.is_friends),
    url(r'^is_entity', view.is_entity),
    url(r'^getEdgeinfo', view.getEdgeinfo),
    
    url(r'^find_pic', view.find_pic),
    url(r'^find_near', view.find_near),
    url(r'^find_path', view.find_path),
    url(r'^get_graph', view.get_graph),
    url(r'^get_spec', view.get_spec),
    url(r'^search_from_spec', view.search_from_spec),
    url(r'^add_word_ops', view.add_word_ops),
    url(r'^deal_process', view.deal_process),
    
    url(r'^$', view.graph),
    url(r'^near', view.near),
    url(r'^path', view.path),
    url(r'^graph', view.graph),
    url(r'^search_spec', view.search_spec),
    url(r'^add_post', view.add_post),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)
