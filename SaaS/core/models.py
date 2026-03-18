from django.db import models
from django.contrib.auth.models import User

class Evento(models.Model):
    organizador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='eventos')
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    data = models.DateField()
    hora = models.TimeField()

    num_convidados = models.IntegerField(help_text="Estimativa de pessoas")
    gasto_comida = models.DecimalField(max_digits=10, decimal_places=2, help_text="Custo para o buffet")
    valor_cobrado = models.DecimalField(max_digits=10, decimal_places=2, help_text="Preço vendido ao cliente")
    total_comida_preparada = models.DecimalField(max_digits=10, decimal_places=2, help_text="Em kg ou unidades")

    def __str__(self):
        return self.nome 


class Convidado(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    codigo = models.CharField(max_length=100) # CharField para aceitar números, letras e caracrteres especiais
    status_de_presenca = models.BooleanField(default=False)


class Refeicao(models.Model):
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE)
    prato = models.CharField(max_length=100)

class RegistroConsumo(models.Model):
    # Relacionamentos
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='consumos')
    convidado = models.ForeignKey(Convidado, on_delete=models.CASCADE)
    refeicao = models.ForeignKey(Refeicao, on_delete=models.CASCADE)
    
    # Dados do Registro
    data_hora = models.DateTimeField(auto_now_add=True)
    repeticao = models.BooleanField(default=False)
    quantidade_estimada = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        help_text="Peso (kg) ou unidades consumidas nesta rodada"
    )

    def save(self, *args, **kwargs):
        # 1. Lógica de Repetição (Apenas para novos registros)
        if not self.pk: 
            ja_comeu = RegistroConsumo.objects.filter(
                evento=self.evento, 
                convidado=self.convidado, 
                refeicao=self.refeicao
            ).exists()
            
            if ja_comeu:
                self.repeticao = True

        # 2. Automação de Presença
        # Se o convidado está consumindo, ele chegou ao evento
        if not self.convidado.status_de_presenca:
            self.convidado.status_de_presenca = True
            # Usamos update_fields para performance, salvando apenas o status
            self.convidado.save(update_fields=['status_de_presenca'])
            
        super(RegistroConsumo, self).save(*args, **kwargs)

    def __str__(self):
        tipo = "Repetição" if self.repeticao else "Primeira vez"
        return f"{self.convidado.nome} - {self.refeicao.prato} ({tipo})"

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