from django.contrib import admin
from django.urls import path
from recaptcha_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('verify/', views.verify_recaptcha, name='verify'),
]
