# forms.py in your Django app

from django import forms

class CodeForm(forms.Form):
    code = forms.CharField(label='Enter your access code', max_length=100)
