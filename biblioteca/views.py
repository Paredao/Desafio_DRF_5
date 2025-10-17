from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Livro, Emprestimo
from .serializers import UserSerializer, LivroSerializer, EmprestimoSerializer, CriarEmprestimoSerializer
from .permissions import IsOwner, IsOwnerOrReadOnly

# Autenticação
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    from django.contrib.auth import authenticate
    username = request.data.get('username')
    password = request.data.get('password')
    
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        })
    return Response({'error': 'Credenciais inválidas'}, status=status.HTTP_400_BAD_REQUEST)

# Livros
class LivroList(generics.ListAPIView):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer
    permission_classes = [IsAuthenticated]

class LivroDetail(generics.RetrieveAPIView):
    queryset = Livro.objects.all()
    serializer_class = LivroSerializer
    permission_classes = [IsAuthenticated]

# Empréstimos
class EmprestimoList(generics.ListCreateAPIView):
    serializer_class = EmprestimoSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CriarEmprestimoSerializer
        return EmprestimoSerializer

    def get_queryset(self):
        # Cada usuário vê apenas seus próprios empréstimos
        return Emprestimo.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        livro = serializer.validated_data['livro']
        # Verifica se o livro está disponível
        if not livro.disponivel:
            return Response(
                {'error': 'Livro não disponível'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cria o empréstimo
        emprestimo = serializer.save(usuario=self.request.user)
        
        # Atualiza disponibilidade do livro
        livro.disponivel = False
        livro.save()

class EmprestimoDetail(generics.RetrieveUpdateAPIView):
    serializer_class = EmprestimoSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        # Cada usuário pode acessar apenas seus próprios empréstimos
        return Emprestimo.objects.filter(usuario=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()
        # Se marcou como devolvido, atualiza a data de devolução
        if instance.devolvido and not instance.data_devolucao:
            from django.utils import timezone
            instance.data_devolucao = timezone.now()
            instance.save()

# Devolução de livro
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def devolver_livro(request, pk):
    try:
        emprestimo = Emprestimo.objects.get(pk=pk, usuario=request.user)
    except Emprestimo.DoesNotExist:
        return Response({'error': 'Empréstimo não encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if emprestimo.devolvido:
        return Response({'error': 'Livro já devolvido'}, status=status.HTTP_400_BAD_REQUEST)

    emprestimo.devolvido = True
    emprestimo.save()

    serializer = EmprestimoSerializer(emprestimo)
    return Response(serializer.data)
