from django import forms

from .models import Mesa


class MesaForm(forms.Form):
    mesa = forms.ModelChoiceField(
        queryset=Mesa.objects.filter(ativa=True),
        empty_label="Selecione a mesa",
        label="Mesa",
        widget=forms.Select(attrs={"class": "campo"}),
        error_messages={
            "required": "Selecione a mesa antes de enviar o pedido.",
            "invalid_choice": "Mesa inválida. Selecione uma mesa da lista.",
        },
    )


class LinhaItemForm(forms.Form):
    quantidade = forms.IntegerField(
        min_value=0,
        max_value=20,
        required=False,
        initial=0,
        label="Quantidade",
        widget=forms.NumberInput(attrs={"class": "campo", "inputmode": "numeric"}),
        error_messages={
            "invalid": "Informe um número inteiro.",
            "min_value": "A quantidade mínima é 0.",
            "max_value": "A quantidade máxima é 20.",
        },
    )
    observacao = forms.CharField(
        max_length=200,
        required=False,
        label="Observação (opcional)",
        widget=forms.TextInput(attrs={"class": "campo"}),
    )