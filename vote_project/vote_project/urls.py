from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^reg/', include('reg_app.urls')),
    url(r'^polls/', include('vote_app.urls')),
    url(r'^admin/', admin.site.urls),
]
