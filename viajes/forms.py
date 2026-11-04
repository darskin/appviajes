from django import forms
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
