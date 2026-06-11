from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'username', 'nome_completo', 'telefone_contato', 'cidade', 'endereco_completo')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cidade'].required = True
        self.fields['endereco_completo'].required = True
        self.fields['endereco_completo'].label = "Endereço Completo"
        self.fields['endereco_completo'].widget.attrs.update({
            'placeholder': 'Ex: Rua das Flores, 123 - Bairro Centro'
        })

from django.contrib.auth.decorators import login_required

from . import services

def register(request):
    """View Magra: Roteia os dados do formulário e delega o registro ao serviço."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            services.efetuar_registro_usuario(request, form)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')
