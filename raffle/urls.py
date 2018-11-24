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
from django.contrib.auth.views import PasswordResetView, password_reset, password_reset_done, password_reset_confirm, password_reset_complete
from app import views
from app.sitemap import Raffle as Site_Raffle
from django.contrib.sitemaps.views import sitemap



urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': {'raffles': Site_Raffle()} }, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^$', views.index, name="home"),
    url(r'^help/$', views.help, name="help"),
    url(r'^terms/$', views.terms, name="terms"),
    url(r'^conditions/$', views.conditions, name="conditions"),
    url(r'^403/$', views.handler403, name="403"),

    # Raffle URLs
    url(r'^raffle/create$', views.Raffle.createRaffle, name="createRaffle"),
    url(r'^myRaffles/$', views.Raffle.myRaffles, name="myRaffles"),
    url(r'^raffle/(?P<id>\w+)$', views.Raffle.details, name="raffleDetails"),
    url(r'^raffle/(?P<id>\w+)/more$', views.Raffle.moreDetails, name="raffleMoreDetails"),
    url(r'^raffles/$', views.Raffle.active, name="raffles"),
    url(r'^raffle/(?P<id>\w+)/finished$', views.Raffle.finished, name="finishedRaffle"),
    url(r'^raffle/(?P<id>\w+)/payment$', views.Raffle.pay, name="payRaffle"),
    url(r'^raffle/(?P<id>\w+)/edit$', views.Raffle.edit, name="editRaffle"),
    # url(r'^raffles/old$', views.Raffle.old, name="rafflesOld"),
    url(r'^buyTicket/(?P<id>\w+)$', views.Raffle.buyTicket, name="buyTicket"),
    # url(r'^addPrivkey/(?P<id>\w+)$', views.Raffle.addPrivkey, name="addPrivkey"), 

    url(r'^login/$', views.User.login, name="login"),
    url(r'^signup/$', views.User.signup, name="signup"),
    url(r'^logout/$', views.User.logout, name="logout"),

    url(r'^addWalletAddress/$', views.User.addWalletAddress, name="addWalletAddress"),
    url(r'^profile/$', views.User.profile, name="profile"),
    url(r'^profile/edit$', views.User.editProfile, name="editProfile"),
    url(r'^api/users/', views.User.getUsers, name="api.users"),
    url(r'^api/user/notifications', views.User.notifications, name="api.usersNotifications"),
    url(r'^api/changePassword/$', views.User.changePassword, name="api.changePassword"),

    url(r'^reset/password_reset', password_reset, 
        {'html_email_template_name': 'registration/password_reset_html_email.html'},
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


handler404 = 'app.views.views.handler404'
handler500 = 'app.views.views.handler500'
handler403 = 'app.views.views.handler403'
handler400 = 'app.views.views.handler400'