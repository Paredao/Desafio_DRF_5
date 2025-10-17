from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Livro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=100)
    disponivel = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.titulo} - {self.autor}"

class Emprestimo(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emprestimos')
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE, related_name='emprestimos')
    data_emprestimo = models.DateTimeField(default=timezone.now)
    data_devolucao = models.DateTimeField(null=True, blank=True)
    devolvido = models.BooleanField(default=False)

    class Meta:
        ordering = ['-data_emprestimo']

    def __str__(self):
        return f"{self.usuario.username} - {self.livro.titulo}"

    def save(self, *args, **kwargs):
        # Atualiza disponibilidade do livro
        if not self.devolvido and not self.data_devolucao:
            self.livro.disponivel = False
            self.livro.save()
        elif self.devolvido and not self.data_devolucao:
            self.data_devolucao = timezone.now()
            self.livro.disponivel = True
            self.livro.save()
        super().save(*args, **kwargs)
