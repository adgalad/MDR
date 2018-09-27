"""raffle URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', views.index, name="index"),
    url(r'^help/$', views.help, name="help"),

    # Raffle URLs
    url(r'^createRaffle/$', views.Raffle.createRaffle, name="createRaffle"),
    url(r'^raffle/(?P<id>\w+)$', views.Raffle.details, name="raffleDetails"),
    url(r'^raffles/$', views.Raffle.active, name="raffles"),
    # url(r'^raffles/old$', views.Raffle.old, name="rafflesOld"),
    url(r'^buyTicket/(?P<id>\w+)$', views.Raffle.buyTicket, name="buyTicket"),
    url(r'^addPrivkey/(?P<id>\w+)$', views.Raffle.addPrivkey, name="addPrivkey"), 

    url(r'^login/$', views.User.login, name="login"),
    url(r'^signup/$', views.User.signup, name="signup"),
    url(r'^logout/$', views.User.logout, name="logout"),

    url(r'^addWalletAddress/$', views.User.addWalletAddress, name="addWalletAddress"),
    url(r'^profile/$', views.User.profile, name="profile"),
    url(r'^editProfile/$', views.User.editProfile, name="editProfile"),

] + staticfiles_urlpatterns()
