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
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete
from app import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^$', views.index, name="home"),
    url(r'^help/$', views.help, name="help"),
    url(r'^terms/$', views.terms, name="terms"),
    url(r'^conditions/$', views.conditions, name="conditions"),

    # Raffle URLs
    url(r'^createRaffle/$', views.Raffle.createRaffle, name="createRaffle"),
    url(r'^myRaffles/$', views.Raffle.myRaffles, name="myRaffles"),
    url(r'^raffle/(?P<id>\w+)$', views.Raffle.details, name="raffleDetails"),
    url(r'^raffle/(?P<id>\w+)/more$', views.Raffle.moreDetails, name="raffleMoreDetails"),
    url(r'^raffles/$', views.Raffle.active, name="raffles"),
    url(r'^raffle/(?P<id>\w+)/finished$', views.Raffle.finished, name="finishedRaffle"),
    # url(r'^raffles/old$', views.Raffle.old, name="rafflesOld"),
    url(r'^buyTicket/(?P<id>\w+)$', views.Raffle.buyTicket, name="buyTicket"),
    url(r'^addPrivkey/(?P<id>\w+)$', views.Raffle.addPrivkey, name="addPrivkey"), 

    url(r'^login/$', views.User.login, name="login"),
    url(r'^signup/$', views.User.signup, name="signup"),
    url(r'^logout/$', views.User.logout, name="logout"),

    url(r'^addWalletAddress/$', views.User.addWalletAddress, name="addWalletAddress"),
    url(r'^profile/$', views.User.profile, name="profile"),
    url(r'^editProfile/$', views.User.editProfile, name="editProfile"),
    url(r'^api/users/', views.User.getUsers, name="api.users"),
    url(r'^api/changePassword/$', views.User.changePassword, name="api.changePassword"),

    url(r'^reset/password_reset', password_reset, 
        name='password_reset'), 
    url(r'^password_reset_done', password_reset_done, 
        {'template_name': 'registration/password_reset_done.html'}, 
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)/$', password_reset_confirm, 
        {'template_name': 'registration/password_reset_confirm.html'},
        name='password_reset_confirm'
        ),
    url(r'^reset/done', password_reset_complete, {'template_name': 'registration/password_reset_complete.html'},
        name='password_reset_complete'),


] + staticfiles_urlpatterns()
