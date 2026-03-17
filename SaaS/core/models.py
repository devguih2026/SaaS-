from django.db import models
from django.contrib.auth.models import User

class Evento(models.Model):
    nome = models.CharField(max_length=100)
    quantidade_convidados = models.IntegerField()
    total_de_comida_preparada = models.DecimalField(max_digits=10, decimal_places=2)
    data_evento = models.DateField()
    organizador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventos')

    def __str__(self):
        return self.nome # Exibe o nome no Admin do Django

class Convidado(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=100) # CharField para aceitar números, letras e caracrteres especiais
    status_de_presenca = models.BooleanField(default=False)

class Refeicao(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    prato = models.CharField(max_length=100)

class RegistroConsumo(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    convidado = models.ForeignKey(Convidado, null=True, blank=True, on_delete=models.CASCADE) # null e blank para que o sistema permita registrar que "alguém comeu" sem necessariamente identificar quem
    refeicao = models.ForeignKey(Refeicao, on_delete=models.CASCADE)
    data_e_hora = models.DateTimeField(auto_now_add=True)
    repeticao = models.BooleanField(default=False) # verificar se a pessoa está comendo pela primeira vez ou repetindo

class Assinatura(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='assinatura'
    )
    plano = models.CharField(max_length=100)
    expiracao = models.DateTimeField()
    limite_de_eventos_por_plano = models.IntegerField()
    ativo = models.BooleanField(default=True)
    valor_mensalidade = models.DecimalField(max_digits=10, decimal_places=2)

    # python manage.py makemigrations

    # python manage.py migrate