# AgriEDGE - Tarım Robotu Simülasyonu

Bu proje, tarım alanlarında otonom hareket eden bir robotun yol planlama ve simülasyonunu gerçekleştiren bir yazılımdır.

## Özellikler

- 2D ve 3D görselleştirme
- Çoklu yol planlama algoritmaları:
  - Adaptif Planlayıcı
  - A* Algoritması
  - RRT (Rapidly-exploring Random Trees)
  - Potansiyel Alan
  - Voronoi Diyagramları
  - Genetik Algoritma
  - Karınca Kolonisi
  - Dalga Yayılımı
- Farklı tarla konfigürasyonları
- Gerçek zamanlı simülasyon
- İnteraktif kullanıcı arayüzü

## Kurulum

1. Gerekli Python paketlerini yükleyin:
```bash
pip install numpy matplotlib
```

2. Projeyi klonlayın:
```bash
git clone https://github.com/kullanici_adi/agri-edge.git
cd agri-edge
```

## Kullanım

Programı çalıştırmak için:
```bash
python farm_robot_simulation.py
```

### Kontroller

- **Algoritma Butonu**: Farklı yol planlama algoritmalarını seçmek için
- **Sonraki Butonu**: Bir sonraki tarla konfigürasyonuna geçmek için
- **Çıkış Butonu**: Simülasyonu sonlandırmak için
- **Mouse**: 3D görünümü döndürmek için

## Proje Yapısı

```
project/
├── planners/
│   ├── __init__.py
│   ├── base_planner.py
│   ├── planner_type.py
│   ├── adaptive_planner.py
│   ├── astar_planner.py
│   ├── rrt_planner.py
│   ├── potential_field_planner.py
│   ├── voronoi_planner.py
│   ├── genetic_planner.py
│   ├── ant_colony_planner.py
│   └── wavefront_planner.py
├── farm_robot_simulation.py
└── path_planner_factory.py
```

## Algoritma Detayları

### Adaptif Planlayıcı
- Önceki başarılı rotaları hafızada tutar
- Benzer durumlar için optimize edilmiş rotalar önerir
- Öğrenme yeteneğine sahiptir

### A* Algoritması
- En kısa yolu bulmak için kullanılır
- Manhattan mesafesi heuristiği kullanır
- Engelleri dikkate alır

### RRT (Rapidly-exploring Random Trees)
- Rastgele örnekleme tabanlı
- Hızlı keşif yeteneği
- Karmaşık ortamlarda etkili

### Diğer Algoritmalar
- Potansiyel Alan: Çekim ve itme kuvvetleri
- Voronoi Diyagramları: Güvenli yol planlama
- Genetik Algoritma: Evrimsel optimizasyon
- Karınca Kolonisi: Sürü zekası
- Dalga Yayılımı: Grid tabanlı planlama

## Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add some AmazingFeature'`)
4. Branch'inizi push edin (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## İletişim

Proje Sahibi - [@DogukanBaygut](https://github.com/DogukanBaygut)

Proje Linki: [https://github.com/DogukanBaygut/AGRIEDGE-PathPlanner](https://github.com/DogukanBaygut/AGRIEDGE-PathPlanner)
