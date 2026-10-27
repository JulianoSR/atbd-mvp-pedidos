from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

GARCOM = "Garçom"
COZINHA = "Cozinha"
DONO = "Dono"
PERFIS = [GARCOM, COZINHA, DONO]

# Opções do menu de cada perfil. O "#" será trocado pelo endereço real
# de cada tela quando ela for construída.
OPCOES_POR_PERFIL = {
    GARCOM: [
        {"titulo": "Novo pedido", "descricao": "Registrar o pedido de uma mesa", "url": "#", "destaque": True},
        {"titulo": "Pedidos da mesa", "descricao": "Ver a etapa de cada pedido", "url": "#", "destaque": False},
    ],
    COZINHA: [
        {"titulo": "Pedidos da cozinha", "descricao": "Ver o que preparar e marcar o andamento", "url": "#", "destaque": True},
    ],
    DONO: [
        {"titulo": "Cardápio", "descricao": "Gerenciar itens e preços", "url": "#", "destaque": True},
    ],
}


def perfil_do_usuario(user):
    """Devolve o perfil (grupo) do usuário, ou None se não tiver nenhum."""
    nomes = set(user.groups.values_list("name", flat=True))
    for perfil in PERFIS:
        if perfil in nomes:
            return perfil
    return None


def perfil_required(*perfis):
    """Exige login e um dos perfis informados. Checagem feita no servidor."""

    def decorador(view):
        @wraps(view)
        @login_required
        def interna(request, *args, **kwargs):
            if perfil_do_usuario(request.user) not in perfis:
                raise PermissionDenied
            return view(request, *args, **kwargs)

        return interna

    return decorador