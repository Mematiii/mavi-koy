# Cape Cove · App Store'a yükleme

Hamarat Haftası ve Pack & Zip ile aynı yol: Capacitor + Codemagic, Mac gerekmez. Apple hesabın ve Codemagic'teki App Store Connect anahtarın (Hamarat ASC) zaten hazır, onları yeniden kullanıyoruz.

| Ayar | Değer |
|---|---|
| Bundle ID | `com.mematiii.capecove` |
| Uygulama adı | Cape Cove: Merge & Restore (ana ekranda "Cape Cove") |
| Sürüm | 1.0 |
| Codemagic iş akışı | **Cape Cove iOS** |

## 1. Bundle ID oluştur
developer.apple.com → Certificates, IDs & Profiles → Identifiers → **+** → App IDs → App → Description: `Cape Cove`, Bundle ID (Explicit): `com.mematiii.capecove` → Capabilities listesinde **Game Center** işaretli olsun → Continue → Register.

## 2. App Store Connect'te uygulamayı aç
appstoreconnect.apple.com → Apps → **+** → New App → iOS · Name: **Cape Cove: Merge & Restore** · Primary language: English (U.S.) · Bundle ID: `com.mematiii.capecove` · SKU: `capecove001` · Full Access.
Ad alınmışsa sonuna bir kelime ekle (örn. "Cape Cove: Seaside Merge"); oyundaki ad değişmez.

## 3. Codemagic'e bağla
1. codemagic.io → **Add application** → GitHub → `mavi-koy` deposu → `codemagic.yaml` kullan.
2. Team settings → codemagic.yaml settings → Code signing identities → iOS provisioning profiles → **Fetch profiles** → `com.mematiii.capecove` için App Store profilini seç (yoksa aynı ekranda oluştur). Sertifika diğer oyunlarla ortak.

## 4. Derle
Uygulamaya gir → **Start new build** → workflow **Cape Cove iOS**. ~20 dk sonra TestFlight'a düşer.

## 5. Game Center sıralamaları (bir kere)
Codemagic → Start new build → workflow **Cape Cove Game Center setup**. İki sıralama oluşturur: `weekly_contest` (haftalık yarış puanı) ve `player_level` (oyuncu seviyesi). Sonra App Store Connect'te sürüm sayfasında **Game Center** kutusunu işaretleyip iki sıralamayı ekle.

## 6. Gizlilik / destek sayfası
`docs/index.html` hazır. Depo herkese açıksa: GitHub → Settings → Pages → Branch `main` / `docs` → Save → adres `https://mematiii.github.io/mavi-koy/` olur. Depo gizliyse Hamarat'taki gibi ayrı, herkese açık küçük bir depo (örn. `capecove-gizlilik`) açıp bu dosyayı oraya koyarız.

## 7. İncelemeye gönder
- `MAGAZA.md`'deki metinleri yapıştır.
- Ekran görüntüleri: `store/` klasöründeki 5 görsel (1320×2868, 6.9" iPhone).
- App Privacy: **Data Not Collected**.
- Age rating: hepsi None → 4+.
- Pricing: Free.
- Build: TestFlight'taki 1.0 → Add for Review → Submit.

## Güncellemeler
Oyun değişince `www/` güncellenir, Codemagic'te yeniden build. Yeni sürüm numarası için `codemagic.yaml` → `APP_VERSION`.
