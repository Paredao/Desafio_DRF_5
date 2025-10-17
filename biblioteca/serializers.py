from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Livro, Emprestimo
from rest_framework.authtoken.models import Token

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user

class LivroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livro
        fields = ['id', 'titulo', 'autor', 'disponivel', 'created_at']

class EmprestimoSerializer(serializers.ModelSerializer):
    livro_titulo = serializers.CharField(source='livro.titulo', read_only=True)
    livro_autor = serializers.CharField(source='livro.autor', read_only=True)

    class Meta:
        model = Emprestimo
        fields = ['id', 'livro', 'livro_titulo', 'livro_autor', 'data_emprestimo', 
                 'data_devolucao', 'devolvido']
        read_only_fields = ['usuario', 'data_emprestimo', 'data_devolucao']

class CriarEmprestimoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emprestimo
        fields = ['livro']

    def validate_livro(self, value):
        if not value.disponivel:
            raise serializers.ValidationError("Este livro não está disponível para empréstimo")
        return value