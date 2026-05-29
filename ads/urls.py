from django.urls import path
from . import views

app_name = 'ads'

urlpatterns = [
    path('', views.ad_list, name='list'),
    path('meus-anuncios/', views.my_ads, name='my_ads'),
    path('<int:pk>/', views.ad_detail, name='detail'),
    path('<int:pk>/remover/', views.ad_delete, name='delete'),
    path('novo/', views.ad_create, name='create'),
]
