from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('accounts:login'), name='home'),
    path('accounts/', include('accounts.urls')),
    path('lhtc/', include('lhtc.urls')),
    path('bus/', include('bus.urls')),
    path('lostfound/', include('lostfound.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)