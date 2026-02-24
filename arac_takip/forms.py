from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import SurucuProfili, Durak

# 1. ÖZEL KAYIT FORMU (Rol Seçmeli)
class OzellestirilmisKayitFormu(UserCreationForm):
    # Formda ekstra olarak Rol soracağız
    rol = forms.ChoiceField(choices=SurucuProfili._meta.get_field('rol').choices, label="Kayıt Türü", widget=forms.Select(attrs={'class': 'form-select'}))
    first_name = forms.CharField(label="Adınız", required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Soyadınız", required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Profili güncelle
            user.profil.rol = self.cleaned_data['rol']
            
            # Eğer Patron ise kendini otomatik onaylasın (kendi işinin patronu)
            if user.profil.rol == 'patron':
                user.profil.onayli = True
            
            user.profil.save()
        return user

# 2. DURAK KURMA FORMU
class DurakFormu(forms.ModelForm):
    class Meta:
        model = Durak
        fields = ['durak_adi', 'bolge']
        widgets = {
            'durak_adi': forms.TextInput(attrs={'class': 'form-control'}),
            'bolge': forms.TextInput(attrs={'class': 'form-control'}),
        }