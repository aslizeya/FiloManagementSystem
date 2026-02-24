from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Arac, SurusKaydi, Durak, SurucuProfili

# 1. Kullanıcı Profili (Durak Bilgisi)
# Kullanıcı detayına girdiğinde en altta durak bilgisini de gösterir.
class SurucuProfiliInline(admin.StackedInline):
    model = SurucuProfili
    can_delete = False
    verbose_name_plural = 'Sürücü Profili (Durak Bilgisi)'

# 2. Kullanıcı Admin Panelini Güncelleme
class UserAdmin(BaseUserAdmin):
    inlines = (SurucuProfiliInline,)

# Mevcut User panelini devreden çıkarıp bizimkini takıyoruz
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# 3. Araç Admin Paneli
# (Burada 'sahibi' alanını sildik, sadece durak ve plaka var)
class AracAdmin(admin.ModelAdmin):
    list_display = ('plaka', 'marka_model', 'bagli_durak', 'durum')
    list_filter = ('bagli_durak', 'durum')

admin.site.register(Arac, AracAdmin)
admin.site.register(SurusKaydi)
admin.site.register(Durak)