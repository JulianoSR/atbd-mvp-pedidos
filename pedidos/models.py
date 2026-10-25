from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Mesa(models.Model):
    numero = models.PositiveSmallIntegerField(
        unique=True, validators=[MinValueValidator(1)]
    )
    ativa = models.BooleanField(default=True)

    class Meta:
        ordering = ["numero"]

    def __str__(self):
        return f"Mesa {self.numero}"


class ItemCardapio(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    preco = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )
    disponivel = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Pedido(models.Model):
    class Status(models.TextChoices):
        VALIDANDO = "validando", "Validando"
        EM_PROCESSO = "em_processo", "Em processo"
        ENTREGUE = "entregue", "Entregue"

    mesa = models.ForeignKey(Mesa, on_delete=models.PROTECT, related_name="pedidos")
    garcom = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="pedidos"
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.VALIDANDO
    )
    registrado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-registrado_em"]

    def __str__(self):
        return f"Pedido {self.pk} - {self.mesa}"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="itens")
    item = models.ForeignKey(ItemCardapio, on_delete=models.PROTECT)
    quantidade = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    observacao = models.CharField(max_length=200, blank=True)
    preco_unitario = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f"{self.quantidade}x {self.item}"