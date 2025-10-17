from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('livros/', views.LivroList.as_view(), name='livro-list'),
    path('livros/<int:pk>/', views.LivroDetail.as_view(), name='livro-detail'),
    path('emprestimos/', views.EmprestimoList.as_view(), name='emprestimo-list'),
    path('emprestimos/<int:pk>/', views.EmprestimoDetail.as_view(), name='emprestimo-detail'),
    path('emprestimos/<int:pk>/devolver/', views.devolver_livro, name='devolver-livro'),
]