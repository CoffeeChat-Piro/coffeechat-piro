from django import forms
from .models import CoffeeChat
from .models import Review

class CoffeeChatForm(forms.ModelForm):
    hashtags = forms.CharField(widget=forms.HiddenInput(), required=False)
    content = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = CoffeeChat
        fields = ['job', 'hashtags', 'content']
        

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['content']

class CoffeechatRequestForm(forms.Form):
    requestContent = forms.CharField(max_length=100, required=False, label='RequestContent')

class WayToContect(forms.Form):
    way = forms.CharField(max_length=200, required=False)