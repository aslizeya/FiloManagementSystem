from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# KULLANICI ROLLERİ
ROL_SECENEKLERI = (
    ('surucu', 'Sürücü'),
    ('patron', 'Durak Sahibi'),
)

# 1. DURAKLAR
class Durak(models.Model):
    # Durağın bir sahibi (patronu) olur
    sahibi = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sahip_oldugu_durak', verbose_name="Durak Sahibi")
    durak_adi = models.CharField(max_length=100, verbose_name="Durak Adı")
    bolge = models.CharField(max_length=100, verbose_name="Bölge / Semt")

    def __str__(self):
        return self.durak_adi

# 2. SÜRÜCÜ PROFİLİ (Rol ve Onay Durumu)
class SurucuProfili(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil', verbose_name="Kullanıcı")
    
    # Yeni Eklenenler:
    rol = models.CharField(max_length=10, choices=ROL_SECENEKLERI, default='surucu', verbose_name="Kullanıcı Rolü")
    bagli_durak = models.ForeignKey(Durak, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Çalıştığı Durak")
    
    # Sürücü başvuru yaptı mı, onaylandı mı?
    onayli = models.BooleanField(default=False, verbose_name="Patron Onayı Var mı?")

    def __str__(self):
        return f"{self.user.username} ({self.get_rol_display()})"

# 3. ARAÇLAR
# models.py içindeki Arac sınıfını bununla değiştir:

class Arac(models.Model):
    bagli_durak = models.ForeignKey(Durak, on_delete=models.CASCADE, verbose_name="Bağlı Olduğu Durak")
    plaka = models.CharField(max_length=20, unique=True, verbose_name="Araç Plakası")
    marka_model = models.CharField(max_length=50, verbose_name="Marka ve Model")
    yil = models.IntegerField(verbose_name="Model Yılı")
    guncel_km = models.IntegerField(default=0, verbose_name="Güncel Kilometre")
    durum = models.BooleanField(default=True, verbose_name="Müsait mi?")
    
    # YENİ EKLENEN ALANLAR:
    sahibi_adi = models.CharField(max_length=100, default="Durak Malı", verbose_name="Araç Sahibi Adı")
    sahibi_tel = models.CharField(max_length=20, blank=True, null=True, verbose_name="Sahip Telefon")

    def __str__(self):
        return self.plaka

# 4. SÜRÜŞ KAYITLARI
class SurusKaydi(models.Model):
    arac = models.ForeignKey(Arac, on_delete=models.CASCADE, verbose_name="Araç")
    surucu = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Sürücü")
    alis_zamani = models.DateTimeField(auto_now_add=True)
    alis_km = models.IntegerField()
    teslim_zamani = models.DateTimeField(null=True, blank=True)
    teslim_km = models.IntegerField(null=True, blank=True)
    notlar = models.TextField(null=True, blank=True)

    @property
    def yapilan_mesafe(self):
        if self.teslim_km and self.alis_km:
            return self.teslim_km - self.alis_km
        return 0

# OTOMATİK PROFİL
@receiver(post_save, sender=User)
def profil_olustur(sender, instance, created, **kwargs):
    if created:
        SurucuProfili.objects.create(user=instance)
    instance.profil.save()