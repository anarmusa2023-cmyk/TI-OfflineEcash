# Yüksek TPS'li Açık Blockchain Projesi: Tasarım Taslağı

Bu belge sesli konuşmalarda birlikte oluşturulan fikirleri toplar. Henüz prototipi yoktur; her bölüm test edilmesi gereken bir tasarım hipotezidir.

## 1. Amaç

- Sui ve Aptos'tan kat kat yüksek TPS (hedef: 5x-10x)
- Bitcoin seviyesinde güvenlik hedefi, ancak iş kanıtı (enerji israfı) olmadan
- Telefon dahil herkesin küçük bir cihazla katkı verebildiği, açık ve merkeziyetsiz ağ
- Büyük oyuncuların (zengin kişiler, çok cihazlı sahipler) ağı ele geçirememesi
- Hedef: işlem ücretinin (gas) sıfır olması

## 2. Hız Katmanı: 60 Renkli Paralel Zincir

- Ağ, 60 "renk" adı verilen paralel zincirden oluşur. Her renk kendi işlemlerini bağımsız işler.
- Dışarıdan bakınca kullanıcı için tek bir zincir gibi davranmalıdır (arka planda çalışır, kullanıcı rengi görmez).
- **Renk ataması:** gönderen adresi + ağın ortak "global tur" sayacı kullanılarak hesaplanır. Böylece ilişkili işlemler aynı renkte buluşur, ilişkisiz işlemler paralel akar.
- **Global tur:** her turun özeti bir öncekine kriptografik olarak bağlıdır. Hiçbir cihazın yerel saatine veya "titreşimine" bağlı değildir. Amaç, saat senkronizasyon sorununu ortadan kaldırmaktır. Hedef ritim yaklaşık 20 ms/tur (tur numarası mod 60 = renk ritmi).
- **Titreşim fikrinin rolü:** yerel donanım hızı zamanı belirlemek için değil, node'un ne kadar hızlı yanıt verdiğini ölçmek (gecikme kanıtı) için kullanılabilir.

## 3. Doğrulama Katmanı

- İşlemleri taşıyan node'lar ile onaylayan **validator** node'ları ayrı roller olarak ayrılır.
- Her işlem için havuzdan **rastgele 4 validator** çağrılır; **4'ten 3'ünün** onayı işlemi kesinleştirir (biri çevrimdışı olsa sistem tıkanmaz).
- Seçim, işlem kimliğinin hash'inden türetilen tohumla **VRF** (doğrulanabilir rastgele fonksiyon) kullanılarak yapılır. Kimse kendi tanıklarını seçemez.
- Seçilen 4 validator'ın kimliği, onay tamamlanmadan hemen öncesine kadar gizli tutulur (hedefli DDoS'u engellemek için).

## 4. Validator Seçimi ve Merkezileşmeyi Önleme

- Temel model: **hisse kanıtı (proof of stake)**. Validator olmak için coin kilitlenir; kötü davranan validator'ın coin'i yakılır (slashing).
- Validator sayısı sınırlıdır (ör. ~100), ama koltukları kimin dolduracağına ağ karar verir (stake + VRF), kurucular değil.
- **Süreli koltuk:** validator görevi 1-6 saat gibi sınırlı sürelidir, sonra yeniden stake gerekir. Aynı cüzdan art arda iki dönem validator olamaz (zorunlu rotasyon).
- **Cihaz başına bir validator:** donanım tabanlı cihaz doğrulaması (güvenilir yürütme ortamı / donanım imzası) ile bir fiziksel cihazda yüzlerce sahte validator açılması engellenir.
- Zenginlerin baskın olmasına karşı değerlendirilen ek araçlar: karekök ağırlıklandırma, tek cüzdan/grup için stake üst sınırı, delegasyon.

### 4.1 Mobil Madencilik ve Ödül Modeli

- **Kilit süresi ile validator koltuğu ayrıdır:** kullanıcı 24 saatte bir "mining" düğmesine dokunarak seçtiği miktarda coin kilitler ve validator havuzuna girer. Kısa süreli (1-6 saat) koltukları VRF otomatik dağıtır; kullanıcı saat başı işlem yapmaz.
- **Düğme tek başına kanıt değildir:** botları engellemek için dokunuş, cihaz doğrulamasıyla (donanım imzası) birlikte geçerli sayılır.
- **Ödül formülü:** cihaz başına tek ödül payı; pay, kilitlenen miktarın karekökü ile orantılıdır ve sayılan miktar için bir üst sınır vardır. Coin'i çok cüzdana bölmek ek ödül getirmez, çünkü ödül cihaz başınadır.
- **Çevrimdışı telefonlar:** seçildiği anda çevrimdışı olan mobil cihaz için hafif ödül kesintisi uygulanır; coin yakma (slashing) yalnızca gerçek kötü niyet durumları için saklanır.

## 5. Güvenlik Önlemleri

- **Renkler arası (cross-color) işlemler:** iki aşamalı kesinleşme. Gönderen renk parayı kilitler, alıcı renk onaylar, sonra para düşer. Süre içinde onay gelmezse kilit açılır ve para iade edilir.
- **Uzun menzilli saldırı:** belirli aralıklarla (ör. her ~1000 turda) validator imzalarıyla geri alınamaz checkpoint oluşturulur.
- **Hedefli saldırı:** validator kimliklerinin son ana kadar gizli tutulması (bölüm 3).

### 5.1 Yük Dengesi

- Yoğunluğu eşiği aşan adres (ör. büyük bir borsa) ağ tarafından otomatik olarak birkaç alt-hesaba bölünür; her alt-hesap farklı bir renge düşer, bakiye aralarında paylaştırılır. Kullanıcı hâlâ tek hesap görür.
- Renk yoğunluğu her epoch başında ölçülür; bakiye taşıma maliyetli olduğu için yeniden dengeleme seyrek yapılır.
- Sınır: aynı bakiyeye dokunan işlemler aynı alt-hesapta sıraya girer, tek bir hesabın hızı sonsuz artmaz.

### 5.2 Cihaz Kimliği

- Android/iOS donanım doğrulaması (üretici sertifikası) cihazın gerçek ve rootsuz olduğunu kanıtlar; emülatör ve sahte cihazlar elenir.
- Açık riskler: telefon çiftlikleri (gerçek cihazlar toplu alınabilir), çalınan/kopyalanan anahtarlar (sertifikalar düzenli yenilenmeli, tekrar eden kimlik şüpheli sayılmalı), üretici bağımlılığı (Apple/Google'a güven, tam merkeziyetsizlikten ödün).

### 5.3 Sybil Saldırısına Karşı Katmanlı Savunma

Tek başına hiçbiri yeterli değildir; birlikte saldırının maliyetini kazancının üzerine çıkarmayı hedefler.

1. **Kademeli ödül:** ödüller hemen çekilemez, birkaç hafta boyunca yavaş yavaş açılır.
2. **Cihaz yaşı ve itibar:** yeni cihaz küçük ağırlıkla başlar, ağda temiz geçirdiği her ay ağırlığı artar.
3. **Komite çeşitliliği:** bir işlem için seçilen 4 validator aynı IP aralığından veya aynı ülkeden olamaz.
4. **Davranış tutarlılığı:** aynı anda aynı kalıpla uyanan, aynı saatlerde aktif cihaz kümeleri istatistiksel olarak şüpheli işaretlenir.
5. **Kişilik kanıtı (ilk aşamada kullanılmaz):** biyometrik veya sosyal doğrulama en güçlü korumayı sağlar ama gizlilik ve merkezileşme sorunları getirir.

### 5.4 Kuantum Direnci

- Authenticator tarzı ortak sır kodları blockchain'de çalışmaz (doğrulayıcı herkes olduğu için sır paylaşılmış olur). "Her işleme özgü tek kullanımlık kod" sezgisinin gerçek karşılığı hash tabanlı imzalardır.
- **Varsayılan imza:** ML-DSA (kafes tabanlı, NIST standardı). **Kritik hesaplar için opsiyonel:** SLH-DSA (hash tabanlı, yalnızca hash fonksiyonlarına dayanır).
- **Bedel:** bu imzalar bugünkülerden çok büyüktür (yaklaşık 2-3 KB'tan 10 KB'ın üstüne), bant genişliği ve validator yükü artar, TPS hedefini etkiler.
- **Ek önlemler:** adres her kullanımdan sonra yenilenir (açık anahtar harcanana kadar gizli kalır); imzalar toplu (aggregate) doğrulanır.

### 5.5 Depolama ve Ağ Hacmi

Hedef: ağ verisi gigabaytlarca büyümemeli, sıradan telefonlar node çalıştırabilmeli.

- **Geçmişi budama:** checkpoint'ten önceki işlemler ve imzalar telefonlardan silinir (büyük kuantum imzalarının yükünü de azaltır).
- **Renk başına depolama:** her telefon yalnızca atandığı rengin durumunu tutar; yük kabaca 60 kat azalır.
- **Hafif kanıtlar:** validator, tüm durumu tutmak yerine işlemle gelen küçük bir Merkle kanıtıyla doğrulama yapar.
- **Durum süre aşımı (state expiry):** kullanılmayan hesaplar bir süre sonra arşive alınır; bakiye büyümesi sınırlanır (tamamen sıfırlanamaz).
- **Gönüllü arşiv node'ları:** eski veriyi isteyenler için ayrı node'lar.
- **İleri aşama:** sıfır-bilgi kanıtıyla zincirin sabit boyutlu bir kanıta sıkıştırılması (Mina benzeri); hesaplaması ağır olduğu için sonraya bırakıldı.

### 5.6 İki Katmanlı Node Yapısı

- **Hafif node (mobil cihazlar):** az depolama kullanır, yalnızca atandığı rengin durumunu tutar, validator olarak çalışır.
- **Tam node (bilgisayarlar):** tüm ağ geçmişini ve işlem verisini saklar, gerektiğinde hafif node'larla senkronize olur.
- **Güven kaynağı checkpoint'tir:** hafif node, tam node'a körü körüne güvenmez; aldığı veriyi validator imzalı checkpoint ve Merkle kanıtıyla kendisi doğrular.
- **Tam node ek güç kazanmaz:** validator hakkı cihaz başına birdir; bilgisayarın oy gücü telefondan fazla değildir. Tam node'lar yalnızca veri tutar ve sunar.
- **Teşvik:** ücretsiz ağda geçmişi saklamak maliyetlidir; veri sunan tam node'lara küçük bir ödül payı ayrılır, aksi halde zamanla bırakabilirler.

## 6. Açık Sorular (henüz çözülmedi)

1. **Sıfır ücret ekonomisi:** spam nasıl önlenecek, validator'lara ne teşvik verilecek? (enflasyon, sponsorlu ücret, işlem başı stake, rate limiting seçenekleri var)
2. **Yük dengesi:** bazı adresler (ör. büyük bir borsa) çok işlem yapınca tek renk tıkanabilir. Yoğun adresleri alt-renklere kaydırmak gerekebilir.
3. **Cihaz kimliği:** donanım doğrulaması her cihazda eşit güvenilir değil, taklit riski var.
4. **Kuantum direnci:** kafes tabanlı gibi post-quantum imza algoritmaları seçilmeli.
5. **Gerçek TPS:** kağıt üzerinde 60 x tek zincir kapasitesi yüksek çıkar, ama cross-color işlemler, ağ gecikmesi ve senkronizasyon bu rakamı düşürür. Ancak simülasyon/prototip ile ölçülebilir.
6. **Cihaz başına bir validator ile "herkes eşit" hedefi:** Sybil direnci tam çözülmüş değil.
7. **AI'ın konsensüse katılması:** deterministik ve bağımsız doğrulanabilir olmadığı için konsensüs kararında kullanılmamalı; yardımcı analiz rolünde düşünülebilir.

## 7. Önerilen Sonraki Adımlar

1. Renk atama formülünü ve global tur mekanizmasını netleştirmek
2. Küçük bir simülasyon yazıp (ör. 60 şerit, rastgele işlem yükü) yük dengesini ve cross-color maliyetini ölçmek
3. Validator seçimi için VRF + stake + rotasyon kurallarını detaylandırmak
4. Ücretsiz ağ için ekonomik modeli tasarlamak
5. Kuantum dirençli imza seçimini araştırmak