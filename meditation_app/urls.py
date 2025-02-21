"""
URL configuration for meditation_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.views.generic.base import RedirectView
from django.views.static import serve
from django.http import HttpResponse
import boto3
from botocore.exceptions import ClientError

def serve_sw(request):
    if settings.DEBUG:
        return serve(request, 'sw.js', document_root=settings.STATIC_ROOT)
    else:
        try:
            s3 = boto3.client('s3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            response = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key='sw.js')
            content = response['Body'].read().decode('utf-8')
            return HttpResponse(content, content_type='application/javascript')
        except ClientError as e:
            return HttpResponse(status=404)

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'meditation/images/favicon-32x32.png', permanent=True)),
    path('setlang/', set_language, name='set_language'),
    path('sw.js', serve_sw, name='service-worker'),
]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
)

urlpatterns += i18n_patterns(
    path('', include('meditation.urls')),
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
