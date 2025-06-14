from django import forms
from .models import User 
from django.contrib.auth import authenticate
from .models import Collection
from .models import Content

class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label='Имя пользователя',
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите имя',
            'autocomplete': 'off'
        })
    )
    email = forms.EmailField(
        label='Электронная почта',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Введите email',
            'autocomplete': 'off'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введите пароль',
            'autocomplete': 'new-password'
        }),
        label='Пароль'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Подтвердите пароль',
            'autocomplete': 'new-password'
        }),
        label='Подтверждение пароля'
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким именем уже существует.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже зарегистрирован.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Пароли не совпадают')
        return cleaned_data
        
class LoginForm(forms.Form):
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите имя',
            'autocomplete': 'off',
            'autocorrect': 'off',
            'autocapitalize': 'off',
            'spellcheck': 'false'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введите пароль',
            'autocomplete': 'new-password',
            'autocorrect': 'off',
            'autocapitalize': 'off',
            'spellcheck': 'false'
        })
    )
    user = None

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        if username and password:
            self.user = authenticate(username=username, password=password)
            if self.user is None:
                raise forms.ValidationError('Неверное имя пользователя или пароль')
            elif not self.user.is_active:
                raise forms.ValidationError('Этот пользователь заблокирован')
        return cleaned_data
    


def create_collection(request):
    if request.method == 'POST':
        form = CollectionForm(request.POST)
        if form.is_valid():
            collection = form.save(commit=False)
            collection.user = request.user
            collection.save()
            return redirect('collections')
    else:
        form = CollectionForm()
    return render(request, 'app/create_collection.html', {'form': form})

class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['collection_name']

class ContentForm(forms.ModelForm):
    class Meta:
        model = Content
        fields = ['title', 'genre', 'category', 'image', 'status', 'rating', 'comment', 'release_year', 'description', 'country', 'director', 'actor']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'comment': forms.Textarea(attrs={'rows': 3}),
            'image': forms.FileInput(attrs={'accept': 'image/*'}),
        }