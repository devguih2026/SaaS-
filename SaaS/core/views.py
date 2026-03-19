from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from .models import Evento, RegistroConsumo

def dashboard_evento(request, evento_id):
    evento = get_object_or_404(Evento, id=evento_id) # # Se o ID não existir, ele mostra uma página de "404 - Não encontrado" 

    # 1. A View busca o evento no banco
    evento = Evento.objects.get(id=evento_id)
    
    # 2. A View faz o cálculo que não está no banco
    lucro = evento.valor_cobrado - evento.gasto_comida
    status_lucro = "Positivo" if lucro > 0 else "Prejuízo"  
    
    # 2. Consumo
    total_consumido = RegistroConsumo.objects.filter(evento=evento).aggregate(Sum('quantidade_estimada'))['quantidade_estimada__sum'] or 0
    repeticoes = RegistroConsumo.objects.filter(evento=evento, repeticao=True).count()
    
    # 3. Previsão (A "mágica" do seu sistema)
    # Se consumiram X para N convidados, quanto consumirão para o total?
    sobra_falta = evento.total_comida_preparada - total_consumido
    
     # 3. A View envia tudo isso para o Front-end
    return render(request, 'dashboard.html', {
        "evento": evento,
        "lucro": lucro,
        "repeticoes": repeticoes,
        "sobra_falta": sobra_falta,
        'status': status_lucro
    })


