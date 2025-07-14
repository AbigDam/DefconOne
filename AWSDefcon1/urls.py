"""Defcon1Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.views.static import serve
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
import sys
from django.conf.urls import handler404, handler500, handler403
sys.setrecursionlimit(100000) 

urlpatterns = [
    path("admin/",admin.site.urls),
    path("", include("AWSDefcon1App.urls")),    
]

urlpatterns += [
    re_path(r'^\.well-known/assetlinks\.json$', serve, {
        'document_root': settings.STATIC_ROOT,
        'path': '.well-known/assetlinks.json',
    }),
]

handler404 = 'AWSDefcon1App.views.error'
handler500 = 'AWSDefcon1App.views.error500'
handler403 = 'AWSDefcon1App.views.error'