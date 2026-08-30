# DLavie Visual

**DLavie Visual** adalah paket visual orisinal untuk Minecraft Bedrock Edition dengan target minimum **iPhone 11**. Paket ini memakai resource-pack API resmi dan menyediakan tiga subpack yang dapat dipilih langsung dari ikon roda gigi paket:

| Preset | Target | Resolusi efek | Karakter |
| --- | --- | ---: | --- |
| Low | FPS/baterai | 32 px | awan ringan, warna lembut |
| Medium | rekomendasi iPhone 11 | 64 px | keseimbangan kualitas dan performa |
| High | kualitas | 128 px | awan lebih detail, warna lebih kaya |

## Batasan penting

Tautan referensi pengguna, **Derivative [main]**, adalah shader Java (Iris/OptiFine) milik DureXXX dan berlisensi *All Rights Reserved*. Karena itu repositori ini **tidak menyalin, membongkar, atau mendistribusikan** kode maupun aset Derivative. Ini adalah implementasi *clean-room* orisinal dengan tujuan visual serupa (langit sinematik, warna alam, matahari/bulan yang lebih halus).

Minecraft Bedrock retail di iOS menggunakan RenderDragon dan tidak menyediakan pipeline shader Java. Karena itu port fitur 1:1/“100%” tidak mungkin lewat resource pack resmi. Paket ini sengaja memilih jalur resmi agar dapat diimpor tanpa jailbreak, injector, atau executable pihak ketiga, serta lebih stabil setelah pembaruan Minecraft.

## Instalasi iPhone/iPad

1. Unduh `DLavie-Visual.mcpack` dari hasil build/release.
2. Buka berkas melalui aplikasi **Files**, lalu pilih Minecraft.
3. Di Minecraft, buka **Settings → Global Resources → My Packs**.
4. Aktifkan **DLavie Visual**, tekan ikon roda gigi, lalu pilih Low, Medium, atau High.
5. Mulai ulang dunia bila preset diganti. Medium direkomendasikan untuk iPhone 11.

### Tips stabilitas

- Gunakan jarak render 8–12 chunk pada iPhone 11.
- Matikan antialiasing bila perangkat panas atau baterai cepat turun.
- Jangan menumpuk paket lain yang mengganti `textures/environment/*` atau colormap.
- Turunkan ke Low saat merekam layar; naikkan ke High hanya bila frame time stabil.

## Build dan validasi

Persyaratan: Python 3 dan `zip`.

```bash
./tools/build.sh
```

Script build otomatis membuat seluruh PNG, memvalidasi struktur paket, lalu mengemasnya. Hasil build ada di `dist/DLavie-Visual.mcpack`.

PNG dan folder `dist/` sengaja tidak dilacak Git karena semuanya merupakan keluaran deterministik dari `tools/generate_assets.py`. Dengan begitu pull request hanya berisi source code teks dan tetap dapat diproses oleh sistem review yang tidak mendukung file biner. Untuk hanya membuat atau memeriksa aset secara manual, jalankan:

```bash
python3 tools/generate_assets.py
python3 tools/validate_pack.py
```

## Hak cipta dan kanal

Copyright © 2026 DLavie. Seluruh kode dan aset **orisinal dalam proyek ini** dilindungi hak cipta DLavie; lihat [LICENSE](LICENSE). Informasi, demo, dan pembaruan tersedia di kanal YouTube **DLavie**.

Nama Minecraft adalah milik Mojang/Microsoft. Proyek ini tidak berafiliasi dengan Mojang, Microsoft, CurseForge, atau pembuat Derivative.
