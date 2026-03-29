from django.urls import path
from . import views

urlpatterns = [
    # O 'dashboard/<int:evento_id>/' é o que aparece no navegador.
    # O 'views.api_dashboard_evento' é a função que você escreveu.
    # O 'name="dashboard"' é o apelido para usar no HTML.
   # 1. LISTAGEM E CADASTRO (Ações Gerais)
    path('api/eventos/', views.listar_eventos, name='listar_eventos'),
    path('api/eventos/novo/', views.cadastrar_evento, name='cadastrar_evento'),
    
    # 2. AÇÕES EM UM EVENTO ESPECÍFICO (ID necessário)
    path('api/eventos/<int:evento_id>/', views.detalhe_evento, name='detalhe_evento'),
    path('api/eventos/<int:evento_id>/editar/', views.editar_evento, name='editar_evento'),
    path('api/eventos/<int:evento_id>/deletar/', views.deletar_evento, name='deletar_evento'),
    path('api/eventos/<int:evento_id>/dashboard/', views.api_dashboard_evento, name='dashboard'),
]