from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Choice, Destino


class DestinoForm(forms.ModelForm):

    class Meta:
        model = Destino
        fields = ['nombre', 'descripcion', 'presupuesto']
        labels = {
            'nombre': 'Nombre del Destino Místico',
            'descripcion': 'Descripción de la Experiencia',
            'presupuesto': 'Presupuesto Estimado ($ COP)',
        }
        widgets = {
            'nombre': forms.TextInput(
                attrs={
                    'placeholder': 'Ej. Peña de Juaica, Tabio',
                    'class': 'form-control',
                }
            ),
            'descripcion': forms.Textarea(
                attrs={
                    'placeholder': (
                        'Describe la experiencia mística, nivel de dificultad y'
                        ' ruta...'
                    ),
                    'rows': 4,
                    'class': 'form-control',
                }
            ),
            'presupuesto': forms.NumberInput(
                attrs={
                    'placeholder': '100000',
                    'class': 'form-control',
                }
            ),
        }


class ChoiceForm(forms.ModelForm):

    class Meta:
        model = Choice
        fields = ['choice_text']
        labels = {'choice_text': 'Nueva opción'}


class RegistroForm(UserCreationForm):
    """Registro de cuenta; el rol de viajero se asigna en la vista."""

    class Meta(UserCreationForm.Meta):
        fields = ('username',)


class ItinerarioForm(forms.Form):
    dias = forms.IntegerField(
        label='Número de días', min_value=1, max_value=14, initial=2,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
