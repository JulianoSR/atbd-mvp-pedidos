from django.urls import path

from . import views

urlpatterns = [
    path("", views.menu, name="menu"),
    path("pedidos/novo/", views.novo_pedido, name="novo_pedido"),
]