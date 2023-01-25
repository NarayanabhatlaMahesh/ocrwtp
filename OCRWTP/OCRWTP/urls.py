"""OCRWTP URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.urls import path
from interface import views
from django.conf import settings

from django.conf.urls.static import static


urlpatterns = [
    path('', views.user.home),
    path('upload/', views.user.upload,name='upload'),
    path('upload/UploadFile/',views.user.upload_file,name='UploadFile'),
    path('upload/UploadFile/extracte',views.user.extracte,name='extracte'),
    path('upload/UploadFile/summarize',views.user.summarize,name='summarize'),
    path('upload/UploadFile/translate',views.user.translate,name='translate'),
    path('upload/view_upload/',views.user.view_upload,name='view_upload'),
    path('upload/view_extracted',views.user.view_extracted,name='extracte'),
    path('upload/view_upload/summarize',views.user.summarize,name='summarize'),
    path('upload/view_upload/extracte/summarize/translate',views.user.translate,name='translate'),
    path('upload/view_translations/',views.user.view_translations,name='view_translations'),
    path('upload/view_summaries/',views.user.view_summaries,name='view_summaries'),
    path('upload/view_upload/translate',views.user.translate,name='translate')
]