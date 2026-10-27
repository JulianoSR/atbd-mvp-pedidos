from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .perfis import OPCOES_POR_PERFIL, perfil_do_usuario


@login_required
def menu(request):
    perfil = perfil_do_usuario(request.user)
    contexto = {
        "perfil": perfil,
        "opcoes": OPCOES_POR_PERFIL.get(perfil, []),
    }
    return render(request, "pedidos/menu.html", contexto)