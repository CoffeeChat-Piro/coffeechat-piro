from django import forms
from .models import User

class CustomUserChangeForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'input-field',
            'placeholder': '이름을 입력하세요'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'input-field',
            'placeholder': '이메일을 입력하세요'
        })
    )
    cohort = forms.ChoiceField(
        choices=[(str(x), str(x)) for x in range(21, 24)],  # 21~23기
        widget=forms.Select(attrs={
            'class': 'input-field'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'cohort']