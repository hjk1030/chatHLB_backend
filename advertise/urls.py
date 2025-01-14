from django.urls import path,include
import advertise.views as views

urlpatterns = [
    path('upload', views.upload),
    path('info/<id>', views.getinfo),
    path('list', views.getlist),
]