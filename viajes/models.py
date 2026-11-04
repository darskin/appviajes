from django.db import models


class Destino(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    presupuesto = models.PositiveIntegerField()

    def __str__(self):
        return self.nombre


class Choice(models.Model):
    destino = models.ForeignKey(Destino, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text
