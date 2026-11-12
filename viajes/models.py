from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Destino(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    presupuesto = models.PositiveIntegerField(
        validators=[MinValueValidator(1, 'El presupuesto debe ser mayor que cero.')]
    )
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='destinos',
    )

    def __str__(self):
        return self.nombre

    def puede_gestionar(self, user):
        """El administrador gestiona todo; el viajero solo sus propios destinos."""
        if not user.is_authenticated:
            return False
        return user.is_staff or self.propietario_id == user.id


class Choice(models.Model):
    destino = models.ForeignKey(Destino, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        return self.choice_text


class Voto(models.Model):
    """Un voto por usuario y destino (RF-07); se puede cambiar de opción."""

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    destino = models.ForeignKey(Destino, on_delete=models.CASCADE)
    opcion = models.ForeignKey(Choice, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'destino'], name='un_voto_por_usuario_y_destino'
            )
        ]

    def __str__(self):
        return f'{self.usuario} -> {self.opcion}'
