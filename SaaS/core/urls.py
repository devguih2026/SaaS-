from django.urls import path
from . import views

urlpatterns = [
    # O 'dashboard/<int:evento_id>/' é o que aparece no navegador.
    # O 'views.api_dashboard_evento' é a função que você escreveu.
    # O 'name="dashboard"' é o apelido para usar no HTML.
    path('dashboard/<int:evento_id>/', views.api_dashboard_evento, name='dashboard'),
]