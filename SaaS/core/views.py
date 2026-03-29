from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from .models import Evento, RegistroConsumo, Gasto
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt 


@api_view(['GET'])
def api_dashboard_evento(request, evento_id):
    try:
        evento = Evento.objects.get(id=evento_id)
    except Evento.DoesNotExist:
        return Response({'error': 'Evento não encontrado'}, status=404)
    
    # --- NOVIDADE: Somando os gastos da nova tabela Gasto ---
    total_gastos_variaveis = float(Gasto.objects.filter(evento=evento)
                                   .aggregate(Sum('valor'))['valor__sum'] or 0)
    
    # Lucro = (O que você cobrou) - (Gasto fixo de comida) - (Novos gastos cadastrados)
    lucro = float(evento.valor_cobrado - evento.gasto_comida) - total_gastos_variaveis
    
    total_consumido = float(RegistroConsumo.objects.filter(evento=evento)
                            .aggregate(Sum('quantidade_estimada'))['quantidade_estimada__sum'] or 0)
    
    repeticoes = RegistroConsumo.objects.filter(evento=evento, repeticao=True).count()
    
    dados = {
        "nome": evento.nome,
        "financeiro": {
            "lucro": lucro,
            "gastos_detalhados": total_gastos_variaveis, # Para o colega exibir no Front
            "status": "Positivo" if lucro > 0 else "Prejuízo"
        },
        "consumo": {
            "total_kg": total_consumido,
            "repeticoes": repeticoes,
            "previsao_sobra": float(evento.total_comida_preparada) - total_consumido
        }
    }
    return Response(dados)

@api_view(['POST'])
def cadastrar_gasto(request):
    try:
        dados = request.data
        
        # 1. Validação de presença (Garantir que nada venha vazio)
        if not all(k in dados for k in ('evento_id', 'descricao', 'valor')):
            return Response({"erro": "Campos obrigatórios: evento_id, descricao e valor."}, status=400)

        # 2. Busca do Evento (Tratando o ID)
        try:
            evento = Evento.objects.get(id=dados['evento_id'])
        except (Evento.DoesNotExist, ValueError):
            return Response({"erro": "ID do evento inválido ou não encontrado."}, status=404)

        # 3. Validação do Valor (Proteção Financeira)
        try:
            valor_num = float(dados['valor'])
            if valor_num < 0:
                return Response({"erro": "O valor do gasto não pode ser negativo."}, status=400)
        except (ValueError, TypeError):
            return Response({"erro": "O campo 'valor' deve ser um número válido."}, status=400)

        # 4. Criação Segura
        novo_gasto = Gasto.objects.create(
            evento=evento,
            descricao=dados['descricao'].strip(), # Remove espaços inúteis
            valor=valor_num
        )
        
        # 5. Resposta com Status 201 (Created)
        return Response({
            "mensagem": "Gasto cadastrado com sucesso!",
            "id": novo_gasto.id,
            "detalhes": {
                "evento": evento.nome,
                "valor": valor_num
            }
        }, status=201)

    except Exception as e:
        # Log para você ver no terminal o que houve de inesperado
        print(f"Erro inesperado no cadastro de gasto: {e}")
        return Response({"erro": "Ocorreu um erro interno no servidor."}, status=500)
    
def listar_eventos(request):
    # Ordena pelo ID decrescente (mais novos primeiro)
    eventos = Evento.objects.all().order_by('-id')
    lista_eventos = []
    
    for evento in eventos:
        lista_eventos.append({
            "id": evento.id,
            "nome": evento.nome,  # Padronizado com o Model
            "descricao": evento.descricao,
            "data": evento.data.strftime('%d/%m/%Y') if evento.data else None,
            "hora": evento.hora.strftime('%H:%M') if evento.hora else None,
            "num_convidados": evento.num_convidados,
            "valor_cobrado": float(evento.valor_cobrado)
        })
    
    return JsonResponse(lista_eventos, safe=False)

@csrf_exempt
def cadastrar_evento(request):
    if request.method == 'POST':
        try:
            dados = json.loads(request.body)
            
            # Buscamos um organizador padrão (importante pois o Model exige um User)
            # Se você já tiver login, use request.user
            from django.contrib.auth.models import User
            organizador_padrao = User.objects.first() 

            novo = Evento.objects.create(
                organizador=organizador_padrao,
                nome=dados.get('nome'),
                descricao=dados.get('descricao', ''),
                data=dados.get('data'),
                hora=dados.get('hora', '00:00'),
                num_convidados=dados.get('num_convidados', 0),
                
                # Campos financeiros e técnicos
                gasto_comida=dados.get('gasto_comida', 0.0),
                valor_cobrado=dados.get('valor_cobrado', 0.0),
                total_comida_preparada=dados.get('total_comida_preparada', 0.0)
            )
            
            return JsonResponse({
                'status': 'sucesso', 
                'id': novo.id,
                'mensagem': f'Evento "{novo.nome}" criado com sucesso!'
            }, status=201)

        except Exception as e:
            # O print ajuda você a ver o erro exato no terminal do VS Code
            print(f"Erro no cadastro: {e}") 
            return JsonResponse({'erro': str(e)}, status=400)
            
    return JsonResponse({'erro': 'Método não permitido'}, status=405)
        
@csrf_exempt
def editar_evento(request, evento_id):
    if request.method == 'PUT':
        try:
            evento = Evento.objects.get(id=evento_id)
            dados = json.loads(request.body)
            
            # 1. Atualização de campos de texto (simples)
            evento.nome = dados.get('nome', evento.nome)
            evento.descricao = dados.get('descricao', evento.descricao)

            # 2. Validação de Inteiros (num_convidados)
            try:
                if 'num_convidados' in dados:
                    evento.num_convidados = int(dados['num_convidados'])
            except (ValueError, TypeError):
                return JsonResponse({'erro': 'O número de convidados deve ser um número inteiro'}, status=400)

            # 3. Validação de Decimais (valor_cobrado)
            try:
                if 'valor_cobrado' in dados:
                    valor = float(dados['valor_cobrado'])
                    if valor < 0:
                        return JsonResponse({'erro': 'O valor cobrado não pode ser negativo'}, status=400)
                    evento.valor_cobrado = valor
            except (ValueError, TypeError):
                return JsonResponse({'erro': 'O valor cobrado deve ser um número válido'}, status=400)

            # 4. Salvamento Seguro (Captura erros de formato de data/hora do MySQL)
            try:
                # Se a data vier no formato errado, o save() vai disparar uma exceção
                if 'data' in dados:
                    evento.data = dados['data']
                
                evento.save()
            except Exception as e:
                return JsonResponse({'erro': f'Erro ao salvar dados: Verifique o formato de data (YYYY-MM-DD)'}, status=400)

            return JsonResponse({
                'status': 'sucesso', 
                'mensagem': f'Evento "{evento.nome}" atualizado com sucesso',
                'id': evento.id
            })

        except Evento.DoesNotExist:
            return JsonResponse({'erro': 'Evento não encontrado'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'erro': 'JSON inválido'}, status=400)
            
    return JsonResponse({'erro': 'Método não permitido'}, status=405)
        
@csrf_exempt
def deletar_evento(request, evento_id): # Mude para evento_id
    if request.method == 'DELETE':
        try:
            evento = Evento.objects.get(id=evento_id)
            evento.delete()
            return JsonResponse({'status': 'sucesso', 'mensagem': 'Evento excluído'})
        except Evento.DoesNotExist:
            return JsonResponse({'erro': 'Evento não encontrado'}, status=404)
        
def resumo_evento(request, evento_id):
    try:
        evento = Evento.objects.get(id=evento_id)
        # Busca todos os gastos extras vinculados a este evento na tabela core_gasto
        gastos_extras = Gasto.objects.filter(evento=evento).aggregate(Sum('valor'))['valor__sum'] or 0
        
        total_custo = float(evento.gasto_comida) + float(gastos_extras)
        lucro_estimado = float(evento.valor_cobrado) - total_custo
        
        return JsonResponse({
            'evento': evento.nome,
            'valor_recebido': float(evento.valor_cobrado),
            'custo_total': total_custo,
            'lucro': lucro_estimado,
            'status': 'Lucro' if lucro_estimado > 0 else 'Prejuízo'
        })
    except Evento.DoesNotExist:
        return JsonResponse({'erro': 'Evento não encontrado'}, status=404)
    
def detalhe_evento(request, evento_id):
    try:
        e = Evento.objects.get(id=evento_id)
        dados = {
            "id": e.id,
            "nome": e.nome,
            "descricao": e.descricao,
            "data": e.data.isoformat(), # Formato YYYY-MM-DD que o <input type="date"> entende
            "hora": e.hora.strftime('%H:%M') if e.hora else "00:00",
            "num_convidados": e.num_convidados,
            "gasto_comida": float(e.gasto_comida),
            "valor_cobrado": float(e.valor_cobrado),
            "total_comida_preparada": float(e.total_comida_preparada)
        }
        return JsonResponse(dados)
    except Evento.DoesNotExist:
        return JsonResponse({'erro': 'Evento não encontrado'}, status=404)

@api_view(['GET'])
def api_visao_geral(request):
    total_recebido = Evento.objects.aggregate(Sum('valor_cobrado'))['valor_cobrado__sum'] or 0
    total_custo_fixo = Evento.objects.aggregate(Sum('gasto_comida'))['gasto_comida__sum'] or 0
    total_gastos_variaveis = Gasto.objects.aggregate(Sum('valor'))['valor__sum'] or 0
    
    lucro_total = float(total_recebido) - float(total_custo_fixo) - float(total_gastos_variaveis)
    
    return Response({
        "financeiro_global": {
            "receita_total": float(total_recebido),
            "lucro_total": lucro_total,
            "qtd_eventos": Evento.objects.count()
        }
    })
    




