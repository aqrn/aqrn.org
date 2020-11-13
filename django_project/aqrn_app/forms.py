from django import forms
from django.core.validators import RegexValidator

zip_code_validator = RegexValidator(r"[0-9]{5}", "Enter a 5-digit zip code.")


class ZipCodeForm(forms.Form):
    zip_code = forms.CharField(required=True,
                               max_length=5,
                               validators=[zip_code_validator],
                               widget=forms.TextInput(
                                   attrs={'pattern': '[0-9]{5}',
                                          'placeholder': '55555',
                                          'title': 'Enter a 5-digit numerical zip code',
                                          'type': 'tel'
                                          }))

