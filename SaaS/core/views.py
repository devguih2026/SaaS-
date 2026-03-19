from django.http import JsonResponse
from django.db.models import Sum
from .models import Evento, RegistroConsumo

def api_dashboard_evento(request, evento_id):
    # 1. Busca o evento (ou retorna 404 se não existir)
    try:
        evento = Evento.objects.get(id=evento_id)
    except Evento.DoesNotExist:
        return JsonResponse({'error': 'Evento não encontrado'}, status=404)
    
    lucro = float(evento.valor_cobrado - evento.gasto_comida) # Convertemos para float para o JSON aceitar
    
    total_consumido = float(RegistroConsumo.objects.filter(evento=evento)
                            .aggregate(Sum('quantidade_estimada'))['quantidade_estimada__sum'] or 0)
    
    repeticoes = RegistroConsumo.objects.filter(evento=evento, repeticao=True).count()
    
    dados = {
        "nome_evento": evento.nome,
        "financeiro": {
            "lucro": lucro,
            "status": "Positivo" if lucro > 0 else "Prejuízo"
        },
        "consumo": {
            "total_kg": total_consumido,
            "repeticoes": repeticoes,
            "previsao_sobra": float(evento.total_comida_preparada) - total_consumido
        }
    }
    
    # 4. Entrega o JSON
    return JsonResponse(dados)

    




