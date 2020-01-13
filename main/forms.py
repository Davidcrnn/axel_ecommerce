from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


class CheckoutForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Turing',
        'class': 'form-control checkout-input'
    }))
    prenom = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Alan',
        'class': 'form-control checkout-input'
    }))
    phone = forms.CharField(max_length=10, widget=forms.TextInput(attrs={
        'placeholder': '0145444646',
        'class': 'form-control checkout-input'
    }))
    email = forms.EmailField(widget=forms.TextInput(attrs={
        'placeholder': 'Alan@turing.com',
        'class': 'form-control checkout-input'
    }))
    adresse = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '12 rue de sèvres',
        'class': 'form-control checkout-input'
    }))
    code_postal = forms.CharField(max_length=13, widget=forms.TextInput(attrs={
        'placeholder': '75000',
        'class': 'form-control checkout-input'
    }))
    pays = CountryField(blank_label='(Pays)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100 checkout-input',
        }))
