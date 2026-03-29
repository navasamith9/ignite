from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Add this line for Google OAuth
    path('accounts/', include('allauth.urls')), 
    
    # 2. Update this to point to the new Google Login URL
    path('', lambda request: redirect('/accounts/google/login/'), name='home'),
    
    path('accounts/', include('accounts.urls')),
    path('lhtc/', include('lhtc.urls')),
    path('bus/', include('bus.urls')),
    path('help/', include('helpdesk.urls')),
    path('lostfound/', include('lostfound.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)