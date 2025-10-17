from django.contrib import admin
from .models import Livro, Emprestimo

@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'autor', 'disponivel']
    list_filter = ['disponivel', 'autor']
    search_fields = ['titulo', 'autor']

@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'livro', 'data_emprestimo', 'devolvido']
    list_filter = ['devolvido', 'data_emprestimo']
    search_fields = ['usuario__username', 'livro__titulo']
