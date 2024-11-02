from django import forms
from django.core.validators import MaxLengthValidator, MinLengthValidator
from .models import Person

class PersonForm(forms.Form):
    name = forms.CharField(
        label='이름',
        max_length=20,
        required=True,
        validators=[
            MaxLengthValidator(limit_value=20),
            MinLengthValidator(limit_value=4)
        ]
        )
    age = forms.IntegerField(label='나이', required=True)
    

class PersonModelForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['name','age']
    


CATEGORY_CHOICES = [
    ('new_bra', 'new_bra'),
    ('3w', '3w'),
    ('consen', 'consen'),
    ('sun', 'sun'),
]

class StockFilterForm(forms.Form):
    new_bra = forms.BooleanField(label='new_bra', required=False)
    w3 = forms.BooleanField(label='w3', required=False)
    consen = forms.BooleanField(label='consen', required=False)
    sun = forms.BooleanField(label='sun', required=False)
    