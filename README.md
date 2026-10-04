# DmasterCounter

Aplikasi desktop Windows untuk menghitung kebutuhan pail 15 kg bagi produk dan setiap material produksi.

© 2026 Dominicus Daimon Pradana. All rights reserved. Hak atas aplikasi dan source code ini dipertahankan oleh pemiliknya. Penyalinan, pendistribusian, atau penggunaan komersial memerlukan izin tertulis.

## Menjalankan dari source

Memerlukan Python 3.10 atau lebih baru dengan Tkinter tersedia.

```powershell
python main.py
```

## Perhitungan

- Pail setara = berat (kg) dibagi 15.
- Pail utuh per material = hasil pembagian dibulatkan ke bilangan terdekat; desimal di bawah 0,50 turun, sedangkan 0,50 atau lebih naik.
- Total produk = jumlah berat material yang diisi.
- Pail utuh produk dihitung dari berat total produk dengan aturan pembulatan yang sama. Jumlah ini dapat berbeda dari total pail material karena pembulatan dilakukan per material.
- Baris material kosong diabaikan. Jumlah menerima titik atau koma sebagai tanda desimal.
- Pada halaman pail, dua pratinjau print out di bagian bawah mengikuti nama produk, nama material, dan jumlah kg yang dimasukkan. Pratinjau pail menunjukkan jumlah bulat hasil pembagian kg dengan 15; setiap jumlah positif di bawah 15 kg ditampilkan sebagai 1 pail. Masing-masing pratinjau memiliki tombol **Salin**.
- Halaman **ItemList** mengelola nama produk dan bahan dalam database SQLite lokal (`%LOCALAPPDATA%\\DmasterCounter\\itemlist.db`). Di kolom nama produk atau bahan, ketik potongan nama/akronim lalu tekan Enter. Kolom produk mencari daftar produk dan juga daftar bahan sebagai fallback, sehingga nama yang sudah disimpan di salah satu kategori tetap bisa dipanggil. Jika ada beberapa kecocokan, pilih nama dari daftar yang muncul dengan tombol panah lalu Enter. Contoh: `ymj`, `yell mj`, dan `w mj` dapat mencocokkan **Yellow MJ**; `mj` dapat menampilkan beberapa pilihan.

## Perhitungan formulasi

Pada halaman **Perhitungan Formulasi**, nama bahan dan gramasi acuan tiap bahan diisi manual. Masukkan total produksi target dalam kg; aplikasi menghitung persentase tiap gramasi terhadap jumlah gramasi acuan dan membagi target produksi secara proporsional untuk memperoleh jumlah kg tiap bahan. Contoh gramasi acuan `156, 60, 34, 10, 40` memiliki total acuan 300; untuk target 27 kg, hasilnya 14,04 kg, 5,4 kg, 3,06 kg, 0,9 kg, dan 3,6 kg.

## Membuat executable Windows

Build harus dijalankan pada Windows untuk menghasilkan executable Windows.

```powershell
python -m pip install -r requirements-build.txt
python -m PyInstaller --clean --noconfirm DmasterCounter.spec
```

Executable satu file akan berada di `dist\\DmasterCounter.exe`. Source code aplikasi dan file build tidak diperlukan untuk menjalankan executable tersebut.

## Pengujian

```powershell
python -m unittest discover -s tests -v
```
