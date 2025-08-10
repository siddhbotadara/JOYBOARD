#urls.py - accounts
from django.urls import path
from accounts import views
from django.conf import settings
from django.conf.urls.static import static
import os

urlpatterns = [
    path('', views.index, name='home'),                 
    path('base/', views.base, name='base'),  
    path('login/', views.login_page, name='login-html'),   
    path('logout/', views.logout_page, name='logout-html'),
    path('signup/',views.signup_page, name='signup-html'),
    path('rules/',views.how_to_play_page, name='how_to_play-html'),
    path('contact/',views.contact_page, name='contact-html'),
    path('dashboard/',views.dashboard_page, name='dashboard-html'),
    path('leaderboard/',views.leaderboard_page, name='leaderboard'),
    path('about/',views.about_page, name='about-html'),
    path('privacy/',views.privacy_page, name='privacy-html'),
    path('terms/',views.terms_page, name='terms-html'),
    path('forgotpass/',views.forgotpass_page, name='forgotpass-html'),
    path('changepassword/', views.changepassword_logic, name='changepassword'), 
    path('description/', views.set_description, name='set_description'),
    path('news/', views.news_page, name='news-html'),
    path('download/', views.download_page, name='download-html'),
    path('download/joyboard/', views.download_joyboard_zip, name='download_joyboard'),

    path(settings.API_LOGIN_PATH, views.api_login, name='api-login'),  
    path(settings.API_SUBMIT_SCORE_PATH, views.submit_score, name='submit_score'),
    path(settings.API_GET_CONFIG,views.get_config, name='get-config')
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'static'))