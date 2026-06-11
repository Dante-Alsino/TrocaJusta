from django.contrib.auth import login

def efetuar_registro_usuario(request, form):
    """
    Regra de Negócio: Finaliza o registro de um novo usuário garantindo
    o fluxo de login automático logo após a criação da conta.
    """
    user = form.save()
    login(request, user)
    return user
