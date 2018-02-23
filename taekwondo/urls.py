"""taekwondo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from scoring.views import match, new_fighter, last_match, top, results, scoring, new_scoring, command

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^new/$', match),
    url(r'^reg/$', new_fighter),
    url(r'^$', last_match),
    url(r'^(?P<match_id>\d+)/$', match),
    url(r'^(?P<match_id>\d+)/top/$', top),
    url(r'^(?P<match_id>\d+)/(?P<player_id>\d+)/results/$', results),
    # url(r'^(?P<match_id>\d+)/new$', new_score),
    url(r'^score/(?P<score_id>\d+)/$', scoring),
    url(r'^new_score/(?P<match_id>\d+)/(?P<fighter_id>\d+)/$', new_scoring),
    url(r'^score/(?P<score_id>\d+)/(?P<param>[a-zA-Z0-9_.]+)$', command),

    url('login/', auth_views.LoginView.as_view(template_name='login.html')),
    url('logout/', auth_views.LogoutView.as_view(template_name='logout.html')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    if settings.MEDIA_ROOT:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
