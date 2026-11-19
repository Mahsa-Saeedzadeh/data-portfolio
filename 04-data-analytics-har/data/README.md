# Daten

Die Rohdaten (ca. 1,4 GB) sind nicht im Repository enthalten. So legst du sie ab:

```text
data/
├── kuhar/
│   ├── DESCRIPTION.txt                                   (liegt bei)
│   └── KU-HAR_time_domain_subsamples_20750x300.csv       (317 MB, aus "3.Time_domain_subsamples")
└── har70/
    ├── 501.csv … 518.csv                                 (eine Datei je Proband)
```

| Datensatz | Quelle | Inhalt |
|---|---|---|
| KU-HAR | <https://www.kaggle.com/datasets/niloy333/kuhar> | 20 750 Zeitfenster à 3 s, 18 Aktivitäten, 90 Probanden, Accelerometer + Gyroskop (100 Hz) |
| HAR70+ | <https://www.kaggle.com/datasets/anshtanwar/adult-subjects-70-95-years-activity-recognition> | Rohdaten von 18 Probanden zwischen 70 und 95 Jahren, zwei Sensoren (Rücken, Oberschenkel), 50 Hz |

Das Notebook greift über `DATA_DIR = Path("../data")` auf diese Ordner zu.
