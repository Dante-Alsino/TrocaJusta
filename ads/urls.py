from django.urls import path
from . import views

app_name = 'ads'

urlpatterns = [
    path('', views.ad_list, name='list'),
    path('<int:pk>/', views.ad_detail, name='detail'),
    path('novo/', views.ad_create, name='create'),
]
