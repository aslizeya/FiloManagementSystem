from django.urls import path
from . import views

urlpatterns = [
    # 1. Vitrin Sayfası
    path('', views.anasayfa, name='anasayfa'),

    # 2. Yönetim Paneli
    path('panel/', views.arac_listesi, name='arac_listesi'),

    # 3. Diğer Sayfalar
    path('duraklar/', views.tum_duraklar, name='tum_duraklar'),
    
    path('giris/', views.giris_yap, name='giris_yap'),
    path('cikis/', views.cikis_yap, name='cikis_yap'),
    path('kayit/', views.kayit_ol, name='kayit_ol'),
    
    path('durak-kur/', views.durak_olustur, name='durak_olustur'),
    path('basvur/', views.duraaga_basvur, name='duraaga_basvur'),
    path('onayla/<int:surucu_id>/', views.surucu_onayla, name='surucu_onayla'),
    
    path('arac-ekle/', views.arac_ekle, name='arac_ekle'),
    path('teslim-al/<int:arac_id>/', views.teslim_al, name='teslim_al'),
    path('teslim-et/<int:arac_id>/', views.teslim_et, name='teslim_et'),
    path('gecmis/<int:arac_id>/', views.arac_gecmisi, name='arac_gecmisi'),
    
    # İŞTE UNUTTUĞUMUZ VE HATAYA SEBEP OLAN SATIR BU 👇
    path('satis-yap/<int:arac_id>/', views.arac_satisi, name='arac_satisi'),
    # urls.py içine ekle:
    path('nasil-calisir/', views.nasil_calisir, name='nasil_calisir'),
    # urls.py listesine ekle:
    path('suruculer/', views.suruculer, name='suruculer'),
]