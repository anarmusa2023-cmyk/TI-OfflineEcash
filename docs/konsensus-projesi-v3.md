# Yüksek TPS'li Açık Blockchain Projesi: Tasarım Taslağı (v3)

Bu belge v2 taslağının, kuantum dirençli imza toplulaştırması araştırması ve yeni simülasyon senaryolarıyla (Bölüm 5.4 ve 7) güncellenmiş halidir. Henüz gerçek bir prototip yoktur. Simülasyon rakamları bant genişliği, CPU ve yük modeline dayanan **üst sınır tahminleridir**; varsayımlar Bölüm 7'de listelenmiştir. Bölümlerde **[v2]** ve **[v3]** ile işaretli yerler önceki sürümlere göre değişen kısımlardır.

## 1. Amaç

- Yüksek, **sürdürülebilir** TPS. [v2] Hedef rakamı Bölüm 1.1'deki taban değerlere göre yeniden tanımlandı.
- Bitcoin seviyesinde güvenlik hedefi, ancak iş kanıtı (enerji israfı) olmadan
- Telefon dahil herkesin küçük bir cihazla katkı verebildiği, açık ve merkeziyetsiz ağ
- Büyük oyuncuların (zengin kişiler, çok cihazlı sahipler) ağı ele geçirememesi
- İşlem ücretinin (gas) sıfır olması, spam kota ile sınırlanarak

### 1.1 [v2] Taban değerler ve hedefin yeniden tanımı

Rakamlar Temmuz 2026'da yapılan aramaya dayanır; "TPS" tanımı kaynaklar arasında çok farklıdır:

- **Sui:** 4 Temmuz 2026'da herkese açık bir canlı deneyde tepe 6.086.766 TPS bildirildi. Bu rakam zincir dışı ödeme/durum kanalları ("programmable tunnels", kapanışta mainnet'e yerleşir) ve sponsorlu gas ile elde edildi. Önceki 297.000 TPS rekoru kontrollü test ortamındaydı. Yani zincir üstü, kullanıcı başına işlem sayısıyla doğrudan kıyaslanamaz.
- **Aptos:** Ekim 2024'te mainnet'te 13.367 TPS tepe değeri bildirildi. Mayıs 2026'da bir günde 12,3 milyon işlem rekoru bildirildi; bu ortalama olarak yaklaşık 142 TPS eder (kendi hesabım).

Sonuç: "Sui ve Aptos'tan 5x-10x" ifadesi hangi rakama göre ölçüldüğüne bağlı olarak anlamsızlaşıyor. Önerilen yeni hedef: **kuantum dirençli imzalarla, mobil validator'lı bir ağda, ölçülmüş ve sürdürülebilir 20k-50k TPS**; karşılaştırma tabanı olarak Aptos'un ölçülmüş mainnet tepe değeri ve gerçek günlük ortalamalar kullanılsın, kanal tabanlı rekorlar ayrı tutulsun.

## 2. Hız Katmanı: 60 Renkli Paralel Zincir

- Ağ, 60 "renk" adı verilen paralel zincirden oluşur. Her renk kendi işlemlerini bağımsız işler. Kullanıcı tek zincir görür.
- **Renk ataması:** gönderen adresi + ağın ortak "global tur" sayacı. [v2] Simülasyona göre alıcıların rastgele dağıldığı durumda işlemlerin %98'i cross-color olur; ilişkili adresleri (aynı uygulama, aynı kullanıcı grubu) aynı renge toplayan bir atama formülü cross-color oranını %19'a kadar indirebilir (%80 kümeleme varsayımıyla).
- **Global tur:** her turun özeti bir öncekine kriptografik olarak bağlıdır; yerel saate bağlı değildir. Hedef ritim yaklaşık 20 ms/tur.
- **Titreşim fikrinin rolü:** zamanı belirlemek için değil, node'un yanıt hızını ölçmek (gecikme kanıtı) için.

## 3. Doğrulama Katmanı

- İşlemleri taşıyan node'lar ile onaylayan **validator** node'ları ayrı roller.
- Seçim, işlem hash'inden türetilen tohumla **VRF** ile yapılır; kimse kendi tanıklarını seçemez. Seçilen validator kimlikleri onaydan hemen öncesine kadar gizli kalır.

### 3.1 [v2] İki kademeli onay

- **Hızlı yol (4 kişilik komite, 3 onay):** yalnızca küçük tutarlar için **geçici** onay. %30 saldırgan payında işlem başına ele geçirme olasılığı yaklaşık %8; bu yüzden tutar üst sınırı şarttır.
- **Kesin yol (40 kişilik komite, 27 onay):** işlem ancak burada geri alınamaz olur. Simülasyonda %30 saldırgan payında ele geçirme olasılığı yaklaşık 10⁻¹¹, %40'ta yaklaşık 5·10⁻⁶ çıktı.
- **Çelişen imza cezası:** aynı işlem için çelişen iki onay imzalayan validator'ın stake'i yakılır.

### 3.2 [v2] Toplu sertifika

- [v3] Telefon validator'lar için sertifika boyutu kritiktir: ML-DSA ile 27 imzalık sertifika yaklaşık 89 KB (5 Mbit/s hatta 200 ms bütçesinin %71'i), Falcon-512 oylarıyla yaklaşık 18 KB (%14). Validator koltuğu yalnızca 1-6 saat sürdüğü için Falcon'un uzun ömürlü anahtar kısıtı bu rolde daha az bağlayıcı olabilir; bu bir çıkarımdır ve ayrı bir güvenlik analizi gerektirir.

- Her işlemle validator oyları taşınmaz. Her renk için belirli aralıklarla (200 ms-1 sn) komitenin imzaladığı **tek bir toplu sertifika** (işlem Merkle kökü) yayılır.
- 20 ms'de sertifika yayınlamak bant bütçesini aşar (ML-DSA'da sertifika yaklaşık 89 KB). Hızlı yol bu gecikmeyi kullanıcıdan gizler.

### 3.3 [v2] Yayılım protokolü

- Naif "herkese tam kopya gönder" (push) yayılımı büyük imzalarda ağı çökertir (ML-DSA'da yaklaşık 4,4k TPS).
- **Zorunlu çözüm: hash duyur, eksik işlemi tek kez çek** (Bitcoin'deki `inv`/`getdata` mantığı). ML-DSA'da yaklaşık 45k TPS'e kadar çıkar.
- Bedeli bir ek gidiş-dönüş gecikmesidir; 200 ms sertifika aralığına sığıp sığmadığı ölçülmeli.

## 4. Validator Seçimi ve Merkezileşmeyi Önleme

- Temel model: **hisse kanıtı**; kötü davranan validator'ın coin'i yakılır (slashing).
- Validator sayısı sınırlıdır (ör. ~100); koltukları ağ belirler (stake + VRF).
- **Süreli koltuk:** 1-6 saat, art arda iki dönem yasak (zorunlu rotasyon).
- **Cihaz başına bir validator:** donanım doğrulaması ile.
- Ek araçlar: karekök ağırlıklandırma, stake üst sınırı, delegasyon.

### 4.1 Mobil Madencilik ve Ödül Modeli

- Kilit süresi ile validator koltuğu ayrıdır: kullanıcı 24 saatte bir "mining" düğmesiyle coin kilitler, kısa koltukları VRF dağıtır.
- Düğme tek başına kanıt değildir; cihaz doğrulamasıyla birlikte geçerlidir.
- Ödül cihaz başınadır; kilitlenen miktarın karekökü ile orantılı ve üst sınırlıdır.
- Çevrimdışı telefonlarda hafif ödül kesintisi; slashing yalnızca gerçek kötü niyet için.

### 4.2 [v2] Sıfır ücret ve spam: kota modeli

- **Kota = f(kilitli stake, cihaz itibarı)**, karekök ağırlıklı. Kota cüzdan başına değil **cihaz başına** hesaplanır; cihazsız cüzdanlar çok küçük kotayla başlar (cüzdan bölme açığını kapatmak için).
- Kota aşımı reddedilmez, sıraya alınır; boş turlarda işlenir.
- Validator teşviki: azalan enflasyon takvimi + uzun vadede sponsorlu toplu ücret (uygulama öder). Enflasyonun coin değerine etkisi ayrı bir ekonomik simülasyonla test edilmeli.

## 5. Güvenlik Önlemleri

- **Renkler arası işlemler:** iki aşamalı kesinleşme; zaman aşımında kilit açılır, para iade edilir. [v2] Küçük tutarlar için hızlı yol: alıcı rengin hafif onayıyla anında kullanılabilir, kesinleşme arkadan gelir.
- **Uzun menzilli saldırı:** her ~1000 turda validator imzalı, geri alınamaz checkpoint.
- **Hedefli saldırı:** validator kimliklerinin son ana kadar gizli tutulması.

### 5.1 Yük Dengesi

- Yoğunluğu eşiği aşan adresler alt hesaplara bölünür; her alt hesap farklı bir renge düşer.
- [v2] Simülasyonda sıcak adresleri 8 alt hesaba bölmek en yüklü rengin yükünü yaklaşık 3 kat düşürdü (232 → 82 birim/tur).
- [v2] Büyük gönderenler için **toplu işlem (batching)**: tek imza + tek Merkle kökü ile binlerce çekim.
- Sınır: aynı bakiyeye dokunan işlemler yine sıraya girer; tek hesabın hızı sınırsız artmaz.

### 5.2 Cihaz Kimliği

- Android/iOS donanım doğrulaması emülatör ve rootlu cihazları eler.
- Açık riskler: telefon çiftlikleri, çalınan anahtarlar, üretici bağımlılığı (Apple/Google).
- [v2] Sertifika **tek başına karar verici değil, itibar puanının bir girdisidir**; sertifikasız cihaz da küçük ağırlıkla katılabilir.

### 5.3 Sybil Saldırısına Karşı Katmanlı Savunma

1. Kademeli ödül (haftalar içinde açılır)
2. Cihaz yaşı ve itibar
3. Komite çeşitliliği (aynı IP aralığı/ülke yok)
4. Davranış tutarlılığı analizi
5. Kişilik kanıtı (ilk aşamada kullanılmaz)

### 5.4 Kuantum Direnci

**[v3] Araştırma özeti (Temmuz 2026 aramasına göre):**

- Hiçbir kuantum dirençli imza şeması BLS gibi yerel toplulaştırma sunmuyor. Güncel yöntem, imzaların geçerliliğini kanıtlayan SNARK/STARK tabanlı toplulaştırma (Ethereum tarafında hash tabanlı leanSig + leanMultisig zkVM yaklaşımı; hâlâ araştırma/devnet aşamasında, konuşlandırılmış standart değil).
- STARK ile yüzlerce imzayı yaklaşık 100-200 KB'lık kanıta sıkıştırmak öneriliyor. Küçük imza sayılarında (örn. 27 ML-DSA imzası ≈ 89 KB) kanıt daha büyük kalır; yani komite sertifikası için değil, **işlem imzaları** için anlamlıdır.
- Falcon-512 imzaları yaklaşık 666 bayttır. Bedeli: Seviye I güvenlik (uzun ömürlü hesap anahtarları için uygun görülmüyor), zor ve hataya açık uygulama, FIPS 206'nın Mayıs 2026 itibarıyla henüz kesinleşmemiş olması.
- SLH-DSA'nın hızlı varyantlarında imzalar yaklaşık 17 KB'a çıkar; simülasyonumda küçük varyantı (7,8 KB) kullandım, yani SLH-DSA sonuçları iyimserdi. Yüksek hızlı hatlar için varsayılan olmamalı.
- Hash tabanlı durumlu (stateful) şemalar durum kaybında sahteciliğe açıktır; adres yenileme fikriyle doğal uyum sağlasa da telefonlarda yedek/kayıp riski nedeniyle yalnızca dar, isteğe bağlı rollerde düşünülmeli.

- **Yayımlanmış kanıt üretim ölçümleri:** leanMultisig/leanVM depolarındaki README'lere göre (CPU, M4 Max 48 GB) XMSS imza toplulaştırma yaklaşık 1.000-1.650 imza/sn, kanıt boyutu yaklaşık 120-330 KiB, tepe bellek yaklaşık 7-9 GiB. SPHINCS tabanlı toplulaştırma yaklaşık 200-300 imza/sn. 900 imzalık bir toplu kanıt yaklaşık 0,5-0,8 sn sürüyor; devnet gözlemlerinde küçük yüklerde bile toplulaştırma süresi yaklaşık 1 sn civarında. **Bu ölçümler XMSS içindir, ML-DSA için değil;** ML-DSA'yı zkVM içinde kanıtlamanın maliyeti bu kaynaklarda yok.

**[v3] Karar önerisi:** varsayılan ML-DSA-65 kalsın; imza katmanı değiştirilebilir bir arayüzün arkasında olsun. Telefon oyları için Falcon opsiyonu ve uzun vadede işlem imzalarının STARK ile toplulaştırılması değerlendirilsin.

- Varsayılan imza **ML-DSA**, kritik hesaplar için opsiyonel **SLH-DSA**. Adres her kullanımdan sonra yenilenir.
- [v2] **Ölçülmüş bedel:** aynı modelde Ed25519'a göre yaklaşık 20-25 kat TPS kaybı (ML-DSA), SLH-DSA ek olarak yaklaşık 1,5 kat daha kötü. SLH-DSA bu yüzden yalnızca küçük bir hesap alt kümesi için kalmalı.
- Bant genişliği asıl darboğazdır; CPU'da doğrulama süresi tavan değildir. Bu yüzden imza/işlem boyutunu küçülten her şey (toplu sertifika, budama, ileride sıfır-bilgi kanıtı) doğrudan TPS'e dönüşür.

### 5.4.1 [v3] İmza seçimi: ML-DSA mı, hash tabanlı tek kullanımlık imza mı?

| | ML-DSA-65 | Hash tabanlı (XMSS/W-OTS benzeri) |
|---|---|---|
| Olgunluk | NIST standardı, hazır kütüphaneler | Araştırma önerisi (ör. leanSig), uygulama gerekir |
| İmza boyutu | ~3,3 KB + 1,95 KB açık anahtar | ~2,5 KB civarı |
| Toplulaştırma | Ölçüm yok, maliyet bilinmiyor | Ölçülmüş: ~1.000-1.650 imza/sn/makine |
| Tahmini TPS | 22k-45k (bant sınırı) | Renk başına 2 prover'da ~43k-71k |
| Durum (state) riski | Yok | Var: anahtar yeniden kullanılırsa sahtecilik |
| Adres yenilemeyle uyum | Gerekmiyor | Doğal uyum |
| Cüzdan karmaşıklığı | Düşük | Yüksek (sayaç, kurtarma) |
| Ek altyapı | Yok | Prover rolü (120-240 makine) |

**Karar: şimdi seçme, ölç.**

1. Varsayılan ML-DSA ile başlanır; imza katmanı değiştirilebilir bir arayüzün arkasındadır.
2. Tek bir renkte iki yol prototiplenir: (a) ML-DSA'yı zkVM içinde kanıtlama maliyetinin ölçülmesi, (b) hash tabanlı tek kullanımlık imzayla cüzdan kurtarma akışının denenmesi.
3. **Karar kriteri:** ML-DSA toplulaştırması XMSS'in en az yarısı hızda çıkarsa ML-DSA'da kalınır. Çıkmazsa hash tabanlı opsiyon yalnızca yüksek hacimli hesaplar için açılır.

**Durum yönetimi azaltma fikri (doğrulanmamış, denetim gerektirir):** cüzdan tek bir tohumdan ve sayaçtan türetilir, telefonda sayaç kaybolursa zincirde harcanmış adresler taranarak sayaç yeniden bulunur (HD cüzdan mantığı). Yedekten geri yükleme ve iki cihazda aynı anahtarın kullanılması senaryoları ayrıca tasarlanmalıdır.

### 5.5 Depolama ve Ağ Hacmi

- Geçmişi budama, renk başına depolama, Merkle kanıtları, durum süre aşımı, gönüllü arşiv node'ları.
- İleri aşama: sıfır-bilgi kanıtıyla zincir sıkıştırma (sonraya bırakıldı).

### 5.6 İki Katmanlı Node Yapısı

- **Hafif node (telefon):** yalnızca atandığı rengin durumunu tutar, validator olarak oy verir, sertifikaları Merkle kanıtıyla doğrular.
- **Tam node (bilgisayar/sunucu):** [v2] **işlem taşıma (gossip) görevi bunlarındır** (telefon hattı yetmiyor, Bölüm 7). Oy gücü artmaz; yalnızca veri tutar ve sunar.
- **Teşvik:** veri ve işlem taşıyan tam node'lara ödül payı. Aksi halde taşıma az sayıda büyük oyuncuya kayar ve "telefonla herkes katkı verir" hedefi zayıflar. Bu, tasarımın merkeziyetçilik riski olarak izlenmeli.

## 6. Açık Sorular

1. **Ekonomi:** kota + enflasyon dengesi, tam node teşviki.
2. **Cross-color gecikmesi ve atomiklik:** hızlı yolun güvenlik analizi.
3. **Cihaz kimliği:** üretici bağımlılığı ve telefon çiftlikleri.
4. **Gerçek TPS:** simülasyon üst sınırdır; gecikme, upload tarafı ve validator trafiği modellenmedi.
5. **Cihaz başına bir validator ile Sybil direnci** tam çözülmedi.
6. **AI'ın konsensüse katılması:** deterministik olmadığı için konsensüs kararında kullanılmaz; yalnızca yardımcı analiz.
7. **Tam node merkezileşmesi:** [v2] 100 Mbit/s taşıyıcı varsayımı kaç bağımsız operatörle sağlanabilir?
8. **[v3] Prover rolü:** işlem imzalarını toplulaştırmak yeni bir "kanıt üretici" rolü ve ağır bir hesaplama gerektirir; imzalar yalnızca prover'lara gittiği için merkezileşme baskısı doğar. Yayımlanmış ölçümler XMSS içindir (Bölüm 5.4); ML-DSA için kanıt üretim maliyeti bilinmiyor. Bu, işlem imzası toplulaştırmasının hash tabanlı (XMSS benzeri) imzalara geçişi gerektirebileceği anlamına gelir, bu da durumlu anahtar yönetimi riskini getirir.
9. **[v3] Falcon oyları:** Seviye I güvenliğin 1-6 saatlik koltuk anahtarları için yeterli olup olmadığı ve FIPS 206 kesinleşmesi.

## 7. [v2] Simülasyon Bulguları

Dosya: `konsensus_sim.py` (standart kütüphane, parametreler dosyanın başında).

**Varsayımlar:** 60 renk, 20 ms tur, renk başına 40 birim/tur kapasite, işlem gövdesi 150 B, tam node hattı 100 Mbit/s (telefon 5 Mbit/s), 8 çekirdek, tek imza doğrulama süresi Ed25519 0,05 ms / ML-DSA 0,1 ms / SLH-DSA 0,8 ms, sertifika aralığı 200 ms, fanout 8, Zipf adres dağılımı (s=1,1).

| Bulgu | Sonuç |
|---|---|
| 4'te 3 komite, %30 saldırgan | işlem başına ~%8 ele geçirme |
| 40'ta 27 komite, %30 saldırgan | ~10⁻¹¹ |
| Alıcılar rastgele | işlemlerin %98'i cross-color; kapasite yaklaşık yarıya iner |
| Sıcak adres bölme | en yüklü renk yükü ~3 kat düşer |
| Oy işlemle taşınırsa (ML-DSA, telefon hattı) | 60 renk ~2,4k TPS |
| Toplu sertifika + tam node (ML-DSA) | 60 renk ~134k TPS (dengeli yük üst sınırı) |
| Sıcak renk darboğazı, duyur+çek yayılım | ML-DSA ~45k, SLH-DSA ~29k TPS |
| Naif push yayılım | ML-DSA ~4,4k TPS |
| Gerçekçi ML-DSA aralığı | yaklaşık **22k-45k TPS** (push+pull ↔ duyur+çek) |
| [v3] Falcon oy sertifikası (tam node hattı) | ~%3 kazanç (sertifika bütçenin küçük kısmı) |
| [v3] Falcon oy sertifikası (telefon, 200 ms) | sertifika bütçenin %71'inden %14'üne düşer |
| [v3] İşlem imzaları STARK ile toplu (kanıt 150 KB varsayımı) | bant tavanı ~1,4M TPS; darboğaz **prover hızına** kayar |
| [v3] Prover sınırı (XMSS ölçümleriyle, 1.000-1.650 imza/sn/makine) | renk başına 1 makine ≈ 22k-36k TPS (60 makine); renk başına 2 makine ≈ 43k-71k TPS (120 makine); renk başına 4 makine ≈ 86k-142k TPS (240 makine). Her makine ~7-9 GiB bellek kullanıyor; kesinlesme gecikmesi saniye mertebesinde |

**Modellenmeyenler:** ağ gecikmesi, upload tarafı, validator'ların ayrı trafiği, imza toplulaştırma kazancı, gerçek cross-color atomiklik hataları. Gerçek ağ bu rakamların altında kalacaktır.

## 8. Önerilen Sonraki Adımlar

1. Renk atama formülünü (ilişkili adresleri toplayan) ve global tur mekanizmasını netleştirmek; kümeleme oranını gerçekçi bir iş yüküyle ölçmek.
2. Duyur+çek yayılım gecikmesini 200 ms sertifika aralığıyla birlikte simüle etmek.
3. Validator seçimi için VRF + stake + rotasyon + çelişen imza cezası kurallarını detaylandırmak.
4. Kota/enflasyon ekonomik modelini tasarlamak ve tam node teşvikini içine katmak.
5. [v3] İşlem imzası toplulaştırması: ML-DSA'nın zkVM içinde kanıtlanma maliyetini ölçmek ya da XMSS benzeri hash tabanlı tek kullanımlık imzalara (adres yenileme ile uyumlu) geçişin durum yönetimi riskini incelemek; Falcon oyları için güvenlik analizi.
6. Küçük bir prototip: 1-2 renk, gerçek ML-DSA imzaları, gerçek bant ölçümü.