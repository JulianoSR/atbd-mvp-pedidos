from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .forms import LinhaItemForm, MesaForm
from .models import ItemCardapio, ItemPedido, Mesa, Pedido
from .perfis import COZINHA, GARCOM, perfil_do_usuario


def criar_usuario(nome, perfil):
    usuario = User.objects.create_user(username=nome)
    usuario.groups.add(Group.objects.get(name=perfil))
    return usuario


# ---------------------------------------------------------------- unitários


class ModelosTest(TestCase):
    def test_numero_da_mesa_deve_ser_maior_que_zero(self):
        with self.assertRaises(ValidationError):
            Mesa(numero=0).full_clean()

    def test_numero_da_mesa_deve_ser_unico(self):
        Mesa.objects.create(numero=1)
        with self.assertRaises(ValidationError):
            Mesa(numero=1).full_clean()

    def test_quantidade_acima_de_20_e_recusada(self):
        garcom = criar_usuario("garcom_modelo", GARCOM)
        mesa = Mesa.objects.create(numero=1)
        item = ItemCardapio.objects.create(nome="Suco", preco=Decimal("8.00"))
        pedido = Pedido.objects.create(mesa=mesa, garcom=garcom)
        linha = ItemPedido(
            pedido=pedido, item=item, quantidade=21, preco_unitario=Decimal("8.00")
        )
        with self.assertRaises(ValidationError):
            linha.full_clean()

    def test_status_inicial_do_pedido_e_validando(self):
        garcom = criar_usuario("garcom_status", GARCOM)
        mesa = Mesa.objects.create(numero=2)
        pedido = Pedido.objects.create(mesa=mesa, garcom=garcom)
        self.assertEqual(pedido.status, Pedido.Status.VALIDANDO)


class FormulariosTest(TestCase):
    def test_mesa_e_obrigatoria_com_mensagem_clara(self):
        form = MesaForm({})
        self.assertFalse(form.is_valid())
        self.assertIn(
            "Selecione a mesa antes de enviar o pedido.", form.errors["mesa"]
        )

    def test_mesa_inativa_nao_pode_ser_escolhida(self):
        mesa = Mesa.objects.create(numero=7, ativa=False)
        self.assertFalse(MesaForm({"mesa": mesa.pk}).is_valid())

    def test_quantidade_maxima_e_20(self):
        self.assertFalse(LinhaItemForm({"quantidade": 21}).is_valid())
        self.assertTrue(LinhaItemForm({"quantidade": 20}).is_valid())

    def test_observacao_maxima_e_200_caracteres(self):
        self.assertFalse(
            LinhaItemForm({"quantidade": 1, "observacao": "a" * 201}).is_valid()
        )


class PerfisTest(TestCase):
    def test_perfil_vem_do_grupo(self):
        self.assertEqual(
            perfil_do_usuario(criar_usuario("g1", GARCOM)), GARCOM
        )

    def test_usuario_sem_grupo_nao_tem_perfil(self):
        self.assertIsNone(perfil_do_usuario(User.objects.create_user("sem_perfil")))


# ------------------------------------------------------------- integração


class FluxoDoPedidoTest(TestCase):
    def setUp(self):
        self.mesa = Mesa.objects.create(numero=5)
        self.prato = ItemCardapio.objects.create(
            nome="Prato executivo", preco=Decimal("28.00")
        )
        self.suco = ItemCardapio.objects.create(
            nome="Suco de laranja", preco=Decimal("8.00")
        )
        self.garcom = criar_usuario("garcom_fluxo", GARCOM)
        self.cozinha = criar_usuario("cozinha_fluxo", COZINHA)
        self.url = reverse("novo_pedido")

    def dados(self, mesa=True, prato=0, suco=0, obs=""):
        dados = {
            f"item{self.prato.pk}-quantidade": prato,
            f"item{self.prato.pk}-observacao": obs,
            f"item{self.suco.pk}-quantidade": suco,
            f"item{self.suco.pk}-observacao": "",
        }
        if mesa:
            dados["mesa"] = self.mesa.pk
        return dados

    def test_menu_exige_login(self):
        resposta = self.client.get(reverse("menu"))
        self.assertRedirects(
            resposta,
            f"{reverse('login')}?next={reverse('menu')}",
            fetch_redirect_response=False,
        )

    def test_login_invalido_mostra_mensagem_generica(self):
        resposta = self.client.post(
            reverse("login"), {"username": "ninguem", "password": "errada"}
        )
        self.assertContains(resposta, "Usuário ou senha incorretos.")

    def test_menu_do_garcom_mostra_so_as_opcoes_dele(self):
        self.client.force_login(self.garcom)
        resposta = self.client.get(reverse("menu"))
        self.assertContains(resposta, "Novo pedido")
        self.assertNotContains(resposta, "Pedidos da cozinha")

    def test_cozinha_nao_acessa_novo_pedido(self):
        self.client.force_login(self.cozinha)
        self.assertEqual(self.client.get(self.url).status_code, 403)
        resposta = self.client.post(self.url, self.dados(prato=1))
        self.assertEqual(resposta.status_code, 403)
        self.assertEqual(Pedido.objects.count(), 0)

    def test_pedido_sem_mesa_nao_e_gravado(self):
        self.client.force_login(self.garcom)
        resposta = self.client.post(self.url, self.dados(mesa=False, prato=1))
        self.assertContains(resposta, "Selecione a mesa antes de enviar o pedido.")
        self.assertEqual(Pedido.objects.count(), 0)

    def test_pedido_sem_item_nao_e_gravado(self):
        self.client.force_login(self.garcom)
        resposta = self.client.post(self.url, self.dados())
        self.assertContains(resposta, "Adicione ao menos um item ao pedido.")
        self.assertEqual(Pedido.objects.count(), 0)

    def test_quantidade_acima_do_limite_nao_grava_nada(self):
        self.client.force_login(self.garcom)
        self.client.post(self.url, self.dados(prato=21))
        self.assertEqual(Pedido.objects.count(), 0)
        self.assertEqual(ItemPedido.objects.count(), 0)

    def test_pedido_valido_e_gravado_com_itens_e_status_inicial(self):
        self.client.force_login(self.garcom)
        resposta = self.client.post(
            self.url, self.dados(prato=2, suco=1, obs="Um sem cebola")
        )
        self.assertRedirects(resposta, reverse("menu"))
        pedido = Pedido.objects.get()
        self.assertEqual(pedido.status, Pedido.Status.VALIDANDO)
        self.assertEqual(pedido.garcom, self.garcom)
        self.assertEqual(pedido.mesa, self.mesa)
        self.assertEqual(pedido.itens.count(), 2)
        linha = pedido.itens.get(item=self.prato)
        self.assertEqual(linha.quantidade, 2)
        self.assertEqual(linha.observacao, "Um sem cebola")
        self.assertEqual(linha.preco_unitario, Decimal("28.00"))

    def test_preco_do_pedido_nao_muda_quando_o_cardapio_muda(self):
        self.client.force_login(self.garcom)
        self.client.post(self.url, self.dados(prato=1))
        self.prato.preco = Decimal("35.00")
        self.prato.save()
        linha = ItemPedido.objects.get()
        self.assertEqual(linha.preco_unitario, Decimal("28.00"))

    def test_texto_malicioso_e_guardado_como_texto(self):
        self.client.force_login(self.garcom)
        texto = "'; DROP TABLE pedidos_pedido; --"
        self.client.post(self.url, self.dados(prato=1, obs=texto))
        self.assertEqual(ItemPedido.objects.get().observacao, texto)
        self.assertEqual(Pedido.objects.count(), 1)