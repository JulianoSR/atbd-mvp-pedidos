from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import LinhaItemForm, MesaForm
from .models import ItemCardapio, ItemPedido, Pedido
from .perfis import GARCOM, OPCOES_POR_PERFIL, perfil_do_usuario, perfil_required


@login_required
def menu(request):
    perfil = perfil_do_usuario(request.user)
    opcoes = []
    for opcao in OPCOES_POR_PERFIL.get(perfil, []):
        opcao = dict(opcao)
        if opcao["url"] != "#":
            opcao["url"] = reverse(opcao["url"])
        opcoes.append(opcao)
    return render(request, "pedidos/menu.html", {"perfil": perfil, "opcoes": opcoes})


@perfil_required(GARCOM)
def novo_pedido(request):
    itens = list(ItemCardapio.objects.filter(disponivel=True))
    dados = request.POST if request.method == "POST" else None
    form_mesa = MesaForm(dados)
    linhas = [(item, LinhaItemForm(dados, prefix=f"item{item.pk}")) for item in itens]
    erro_itens = None

    if request.method == "POST":
        mesa_ok = form_mesa.is_valid()
        linhas_ok = all([form.is_valid() for _, form in linhas])
        selecionados = []
        if linhas_ok:
            selecionados = [
                (item, form.cleaned_data)
                for item, form in linhas
                if form.cleaned_data.get("quantidade")
            ]
            if not selecionados:
                erro_itens = "Adicione ao menos um item ao pedido."

        if mesa_ok and linhas_ok and selecionados:
            mesa = form_mesa.cleaned_data["mesa"]
            with transaction.atomic():
                pedido = Pedido.objects.create(mesa=mesa, garcom=request.user)
                ItemPedido.objects.bulk_create(
                    [
                        ItemPedido(
                            pedido=pedido,
                            item=item,
                            quantidade=dados_item["quantidade"],
                            observacao=dados_item.get("observacao", ""),
                            preco_unitario=item.preco,
                        )
                        for item, dados_item in selecionados
                    ]
                )
            messages.success(request, f"Pedido da mesa {mesa.numero} enviado.")
            return redirect("menu")

    contexto = {"form_mesa": form_mesa, "linhas": linhas, "erro_itens": erro_itens}
    return render(request, "pedidos/novo_pedido.html", contexto)