# Cakupan teknis DLavie Visual

Dokumen ini menjelaskan isi paket secara eksplisit agar tidak disalahartikan sebagai
port shader Java.

## Yang benar-benar tersedia

| Fitur | Low | Medium | High | Implementasi |
| --- | ---: | ---: | ---: | --- |
| Tekstur awan | 32 px | 64 px | 128 px | `textures/environment/clouds.png` |
| Tekstur matahari | 32 px | 64 px | 128 px | `textures/environment/sun.png` |
| Atlas delapan fase bulan | 128×64 | 256×128 | 512×256 | `textures/environment/moon_phases.png` |
| Warna rumput | 32 px | 64 px | 128 px | `textures/colormap/grass.png` |
| Warna dedaunan | 32 px | 64 px | 128 px | `textures/colormap/foliage.png` |
| Pilihan kualitas | Ya | Ya | Ya | subpack pada `manifest.json` |

Seluruh PNG dihasilkan saat build sehingga memang tidak terlihat di pull request.
Jalankan `./tools/build.sh`, lalu periksa isi `dist/DLavie-Visual.mcpack` untuk melihat
aset hasil akhirnya.

## Yang tidak tersedia

- shader vertex/fragment Derivative;
- temporal anti-aliasing, volumetric cloud, screen-space reflection, bloom, atau
  color grading berbasis post-process;
- konfigurasi Iris/OptiFine;
- kode atau tekstur milik Derivative;
- jaminan kesamaan visual 100% dengan Derivative.

Shader Java dan resource pack Bedrock bukan format yang setara. RenderDragon pada
Minecraft Bedrock retail iOS tidak menjalankan program GLSL Iris/OptiFine dari
resource pack. Oleh sebab itu, menyalin folder shader Java ke `.mcpack` tidak akan
menghasilkan efek dan justru akan menambah file mati.

## Mengapa tidak menyalin Derivative?

Halaman CurseForge Derivative menyatakan lisensinya **All Rights Reserved**. Tanpa
izin eksplisit pemegang hak, kode dan asetnya tidak boleh disalin atau didistribusikan
ulang dengan nama DLavie. Proyek ini hanya boleh mengembangkan implementasi orisinal
dan tidak boleh mengklaim sebagai port Derivative.

## Jalur pengembangan yang realistis

1. **Resource pack iOS stabil:** lanjutkan paket ini dengan tekstur lingkungan dan
   material orisinal; kompatibilitas paling luas tetapi efek terbatas.
2. **Pipeline grafis Bedrock resmi:** buat implementasi orisinal untuk fitur grafis
   resmi yang tersedia pada versi Minecraft target; dukungan perangkat harus diuji
   langsung dan tidak dapat diasumsikan dari nama iPhone saja.
3. **Port berizin:** hanya dapat dimulai setelah pemegang hak memberikan source dan
   izin port/distribusi tertulis. Walaupun berizin, efek harus ditulis ulang terhadap
   pipeline Bedrock dan hasilnya tidak dapat dijamin identik 100%.
