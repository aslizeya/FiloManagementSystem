from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
from django.http import HttpResponseForbidden
from .models import Arac, SurusKaydi, Durak, SurucuProfili
from .forms import OzellestirilmisKayitFormu, DurakFormu

# --- 1. KARŞILAMA VE GİRİŞ İŞLEMLERİ ---

def anasayfa(request):
    # Eğer kullanıcı zaten giriş yapmışsa, vitrini gösterme, direkt panele at.
    if request.user.is_authenticated:
        return redirect('arac_listesi')
    return render(request, 'landing.html')

def kayit_ol(request):
    if request.method == 'POST':
        form = OzellestirilmisKayitFormu(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('arac_listesi')
    else:
        form = OzellestirilmisKayitFormu()
    return render(request, 'kayit_ol.html', {'form': form})

def giris_yap(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('arac_listesi')
    else:
        form = AuthenticationForm()
    return render(request, 'giris.html', {'form': form})

def cikis_yap(request):
    logout(request)
    return redirect('anasayfa')
# views.py dosyasına ekle:

def nasil_calisir(request):
    return render(request, 'nasil_calisir.html')

# --- 2. ANA YÖNETİM PANELİ (DASHBOARD) ---

@login_required
def arac_listesi(request):
    profil = request.user.profil
    rol = profil.rol
    
    # Varsayılan Boş Değerler
    araclar = []
    durak = None
    basvuru_bekleyenler = []
    tum_duraklar = Durak.objects.all()
    
    # İstatistik Değişkenleri
    istatistikler = {
        'toplam': 0,
        'musait': 0,
        'sahada': 0,
        'surucu_sayisi': 0
    }

    # SENARYO A: PATRON
    if rol == 'patron':
        try:
            durak = request.user.sahip_oldugu_durak
            araclar = Arac.objects.filter(bagli_durak=durak)
            basvuru_bekleyenler = SurucuProfili.objects.filter(bagli_durak=durak, onayli=False)
            
            # İstatistikleri Hesapla
            istatistikler['toplam'] = araclar.count()
            istatistikler['musait'] = araclar.filter(durum=True).count()
            istatistikler['sahada'] = istatistikler['toplam'] - istatistikler['musait']
            istatistikler['surucu_sayisi'] = SurucuProfili.objects.filter(bagli_durak=durak, onayli=True).exclude(user=request.user).count()
            
        except Durak.DoesNotExist:
            durak = None

    # SENARYO B: SÜRÜCÜ
    elif rol == 'surucu':
        durak = profil.bagli_durak
        if durak and profil.onayli:
            araclar = Arac.objects.filter(bagli_durak=durak)
            # Sürücü de istatistikleri görsün
            istatistikler['toplam'] = araclar.count()
            istatistikler['musait'] = araclar.filter(durum=True).count()
            istatistikler['sahada'] = istatistikler['toplam'] - istatistikler['musait']
        else:
            araclar = []

    return render(request, 'arac_listesi.html', {
        'araclar': araclar,
        'durak': durak,
        'rol': rol,
        'onayli': profil.onayli,
        'basvuru_bekleyenler': basvuru_bekleyenler,
        'tum_duraklar': tum_duraklar,
        'istatistikler': istatistikler
    })

# --- 3. DURAK VE PERSONEL İŞLEMLERİ ---

@login_required
def tum_duraklar(request):
    duraklar = Durak.objects.all()
    
    benim_durak = None
    try:
        if request.user.profil.rol == 'patron':
            benim_durak = request.user.sahip_oldugu_durak
        else:
            benim_durak = request.user.profil.bagli_durak
    except:
        pass

    return render(request, 'duraklar.html', {
        'duraklar': duraklar,
        'durak': benim_durak
    })

@login_required
def durak_olustur(request):
    if request.user.profil.rol != 'patron':
        return HttpResponseForbidden("Sadece durak sahipleri durak kurabilir.")
    
    if request.method == 'POST':
        form = DurakFormu(request.POST)
        if form.is_valid():
            durak = form.save(commit=False)
            durak.sahibi = request.user
            durak.save()
            
            request.user.profil.bagli_durak = durak
            request.user.profil.save()
            return redirect('arac_listesi')
    else:
        form = DurakFormu()
    return render(request, 'durak_olustur.html', {'form': form})

@login_required
def surucu_onayla(request, surucu_id):
    try:
        benim_durak = request.user.sahip_oldugu_durak
    except:
        return HttpResponseForbidden("Yetkisiz işlem.")

    surucu_profili = get_object_or_404(SurucuProfili, id=surucu_id)
    
    if surucu_profili.bagli_durak == benim_durak:
        surucu_profili.onayli = True
        surucu_profili.save()
    
    return redirect('arac_listesi')

@login_required
def duraaga_basvur(request):
    if request.method == 'POST':
        durak_id = request.POST.get('durak_id')
        secilen_durak = get_object_or_404(Durak, id=durak_id)
        
        request.user.profil.bagli_durak = secilen_durak
        request.user.profil.onayli = False
        request.user.profil.save()
        
    return redirect('arac_listesi')

# --- 4. ARAÇ İŞLEMLERİ (EKLEME, TESLİM, SATIŞ) ---

# views.py -> arac_ekle fonksiyonunu bununla güncelle:

@login_required
def arac_ekle(request):
    if request.user.profil.rol != 'patron':
        return render(request, 'yetki_yok.html', {'mesaj': 'Sadece durak sahipleri araç ekleyebilir!'})
    
    try:
        durak = request.user.sahip_oldugu_durak
    except:
        return redirect('durak_olustur')

    if request.method == 'POST':
        Arac.objects.create(
            bagli_durak=durak,
            plaka=request.POST.get('plaka'), 
            marka_model=request.POST.get('model'), 
            yil=request.POST.get('yil'), 
            guncel_km=request.POST.get('km'),
            # YENİ BİLGİLERİ KAYDEDİYORUZ:
            sahibi_adi=request.POST.get('sahibi_adi'),
            sahibi_tel=request.POST.get('sahibi_tel')
        )
        return redirect('arac_listesi')
    return render(request, 'arac_ekle.html')

@login_required
def teslim_al(request, arac_id):
    arac = get_object_or_404(Arac, id=arac_id)
    if not request.user.profil.onayli or arac.bagli_durak != request.user.profil.bagli_durak:
        return HttpResponseForbidden("Bu işlem için yetkiniz yok.")
    
    SurusKaydi.objects.create(arac=arac, surucu=request.user, alis_km=arac.guncel_km)
    arac.durum = False
    arac.save()
    return redirect('arac_listesi')

@login_required
def teslim_et(request, arac_id):
    arac = get_object_or_404(Arac, id=arac_id)
    if arac.bagli_durak != request.user.profil.bagli_durak:
        return HttpResponseForbidden()

    if request.method == "POST":
        aktif_kayit = SurusKaydi.objects.filter(arac=arac, teslim_zamani__isnull=True).last()
        yeni_km = int(request.POST.get('guncel_km'))
        if aktif_kayit:
            aktif_kayit.teslim_zamani = timezone.now()
            aktif_kayit.teslim_km = yeni_km
            aktif_kayit.notlar = request.POST.get('notlar')
            aktif_kayit.save()
        arac.guncel_km = yeni_km
        arac.durum = True
        arac.save()
        return redirect('arac_listesi')
    return render(request, 'teslim_et_formu.html', {'arac': arac})

@login_required
def arac_gecmisi(request, arac_id):
    arac = get_object_or_404(Arac, id=arac_id)
    if arac.bagli_durak != request.user.profil.bagli_durak:
        return HttpResponseForbidden()
    gecmis_kayitlar = SurusKaydi.objects.filter(arac=arac).order_by('-alis_zamani')[:5]
    return render(request, 'arac_gecmisi.html', {'arac': arac, 'kayitlar': gecmis_kayitlar})

@login_required
def arac_satisi(request, arac_id):
    arac = get_object_or_404(Arac, id=arac_id)
    
    # GÜVENLİK: Sadece kendi durağının aracını satabilirsin
    try:
        if arac.bagli_durak != request.user.sahip_oldugu_durak:
            return HttpResponseForbidden("Bu aracı satma yetkiniz yok.")
    except:
        return HttpResponseForbidden("Durak sahibi değilsiniz.")

    baska_patronlar = SurucuProfili.objects.filter(rol='patron').exclude(user=request.user)
    
    if request.method == 'POST':
        yeni_sahip_id = request.POST.get('yeni_sahip')
        yeni_sahip_profili = get_object_or_404(SurucuProfili, id=yeni_sahip_id)
        
        try:
            yeni_durak = yeni_sahip_profili.user.sahip_oldugu_durak
            
            # TRANSFER İŞLEMİ
            arac.bagli_durak = yeni_durak
            arac.durum = True 
            arac.save()
            
            # Eski kayıtları temizle
            SurusKaydi.objects.filter(arac=arac, teslim_zamani__isnull=True).delete()
            
            return redirect('arac_listesi')
            
        except Durak.DoesNotExist:
            pass
        
    return render(request, 'arac_satisi.html', {
        'arac': arac, 
        'patronlar': baska_patronlar
    })
# views.py dosyasının EN ALTINA ekle:

@login_required
def suruculer(request):
    # Kullanıcının durağını bul
    try:
        if request.user.profil.rol == 'patron':
             durak = request.user.sahip_oldugu_durak
        else:
             durak = request.user.profil.bagli_durak
    except:
        durak = None

    if not durak:
         return render(request, 'yetki_yok.html', {'mesaj': 'Bir durağa bağlı değilsiniz.'})

    # O durağa bağlı HERKESİ çek (Patron ve Sürücüler)
    calisanlar_profili = SurucuProfili.objects.filter(bagli_durak=durak).select_related('user')
    
    # Listeyi hazırla: Kim hangi araçta?
    surucu_listesi = []
    for profil in calisanlar_profili:
        # Bu kişinin şu an teslim etmediği (aktif) bir sürüşü var mı?
        aktif_surus = SurusKaydi.objects.filter(surucu=profil.user, teslim_zamani__isnull=True).first()
        
        durum_bilgisi = {
            'ad_soyad': f"{profil.user.first_name} {profil.user.last_name}",
            'kullanici_adi': profil.user.username,
            'rol': profil.get_rol_display(), # 'Sürücü' veya 'Durak Sahibi' yazar
            'aktif_arac': aktif_surus.arac.plaka if aktif_surus else None,
            'calisiyor_mu': True if aktif_surus else False,
            'profil_resmi': 'bi-person-circle' # İlerde resim eklersek burası değişir
        }
        surucu_listesi.append(durum_bilgisi)

    return render(request, 'suruculer.html', {'suruculer': surucu_listesi, 'durak': durak})