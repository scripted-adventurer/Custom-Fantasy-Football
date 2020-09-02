from django.conf.urls import include, url, handler400, handler403, handler404, handler500
from django.contrib import admin
from django.urls import path

handler400='data.views.http_400'
handler403='data.views.http_403'
handler404='data.views.http_404'
handler500='data.views.http_500'

urlpatterns = [
  url(r'^api/', include('data.urls')),
  path('admin/', admin.site.urls),
]