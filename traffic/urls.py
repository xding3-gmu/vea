
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings


urlpatterns = [
    path('vea/', include('charts.urls')),
    path('admin/', admin.site.urls),
]

# urlpatterns = [
#     path(r'^$', HomeView.as_view(), name='home'),
#     path(r'^api/$', get_data, name='api-data'),
#     path(r'^admin/', admin.site.urls),

# ]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
