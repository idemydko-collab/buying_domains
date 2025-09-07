from django.urls import path
from . import views

app_name = 'brain'

urlpatterns = [
    path('', views.home, name='home'),
    path('examples/', views.ExampleListView.as_view(), name='example_list'),
    path('api/examples/', views.api_examples, name='api_examples'),
    path('api/domain-status/', views.domain_status, name='domain_status'),
]