from django.contrib import admin

from .models import ItemCardapio, ItemPedido, Mesa, Pedido


@admin.register(Mesa)
class MesaAdmin(admin.ModelAdmin):
    list_display = ("numero", "ativa")


@admin.register(ItemCardapio)
class ItemCardapioAdmin(admin.ModelAdmin):
    list_display = ("nome", "preco", "disponivel")


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "mesa", "garcom", "status", "registrado_em")
    inlines = [ItemPedidoInline]