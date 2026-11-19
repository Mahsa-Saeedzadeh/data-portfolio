# Human Activity Recognition & Behavioral Pattern Analysis (Data Analytics)

Analyse menschlicher Bewegungsmuster aus Smartphone- und Wearable-Sensoren
und Vergleich zweier Altersgruppen. Modulprojekt Data Analytics.

Notebook: [notebooks/har_analysis.ipynb](notebooks/har_analysis.ipynb) ·
Präsentation: [docs/HAR_Praesentation.pptx](docs/HAR_Praesentation.pptx) ·
Projektvorschlag: [docs/Projektvorschlag.docx](docs/Projektvorschlag.docx)

## Fragestellung

Lassen sich Aktivitäten allein aus statistischen Kennzahlen der Sensorsignale
unterscheiden, und wie unterscheiden sich die Bewegungsmuster jüngerer
Probanden (KU-HAR) von denen älterer Menschen (HAR70+)?

## Vorgehen

1. **EDA**: Struktur, Datentypen und Klassenverteilung beider Datensätze;
   Harmonisierung der Aktivitätslabels (ID → Name → Makro-Gruppe aktiv/inaktiv).
2. **Feature-Extraktion**: Zerlegung der 1 800 KU-HAR-Spalten in 6 Sensorkanäle
   (Accelerometer und Gyroskop, je X/Y/Z). Je Kanal Mittelwert, Varianz,
   Standardabweichung und Energie → 24 Features pro Sample.
   Für HAR70+ werden Rohsignale in 3-Sekunden-Fenster (150 Samples bei 50 Hz)
   aggregiert.
3. **Unüberwachtes Lernen**: K-Means (k = 3) auf standardisierten Features,
   PCA-Visualisierung, Kreuztabelle Cluster × Aktivität, Heatmap.
4. **Überwachtes Lernen**: Random Forest für beide Datensätze mit
   Klassifikationsbericht, Konfusionsmatrix und Feature Importance.
5. **Vergleich** der Feature-Verteilungen beider Altersgruppen.

## Zentrale Erkenntnisse

- K-Means bildet ein dominantes Cluster und zwei winzige Ausreißer-Cluster.
  Bewegungsintensität allein trennt die 18 Aktivitäten nicht; die
  Klassenstruktur ist feiner als drei Gruppen.
- Random Forest erreicht auf KU-HAR 92 % Accuracy bei einem gewichteten
  F1-Score von 0,92. Die 24 statistischen Features reichen also aus, um 18
  Aktivitäten zu trennen. Die Fehler konzentrieren sich auf ähnliche Gangarten:
  Walk-backward erreicht nur 0,60, Walk-circle 0,83.
- Auf HAR70+ liegt die Accuracy bei 96 %, der Macro-F1-Score aber nur bei 0,73.
  Häufige Alltagsaktivitäten werden zuverlässig erkannt, seltene Klassen
  deutlich schlechter. Die wichtigsten Features stammen vom Oberschenkelsensor.
- Ältere Probanden zeigen deutlich geringere Varianz und Energie der
  Bewegungen.

## Ausführen

```bash
pip install -r requirements.txt
# Daten gemäß data/README.md ablegen
jupyter notebook notebooks/har_analysis.ipynb
```

Python 3.12, pandas, NumPy, scikit-learn, matplotlib, seaborn.

## Präsentation

[docs/HAR_Praesentation.pptx](docs/HAR_Praesentation.pptx) fasst das Projekt auf
elf Folien zusammen. GitHub kann PowerPoint-Dateien nicht im Browser anzeigen,
deshalb hier der Aufbau:

| Folie | Inhalt |
|---|---|
| 1 | Titel: Analyse menschlicher Bewegungsmuster aus Sensordaten |
| 2 | Projektübersicht und Fragestellung |
| 3 | Die beiden Datensätze im Vergleich |
| 4 | Explorative Datenanalyse: 55 % aktive, 45 % inaktive Samples |
| 5 | Feature Engineering: 1 800 Werte je Sample zu 24 Kennzahlen verdichtet |
| 6 | Clustering mit K-Means und PCA |
| 7–8 | Klassifikation KU-HAR: 92 % Accuracy, F1-Werte je Aktivität |
| 9 | Klassifikation HAR70+: 96 % Accuracy |
| 10 | Datensatzvergleich: Alter, Datentyp, Performance, Feature-Fokus |
| 11 | Ergebnisse und Fazit |

## Struktur

```text
notebooks/har_analysis.ipynb   Analyse mit Erläuterungen und Ergebnissen
data/                          Download-Anleitung und Datensatzbeschreibung
docs/                          Präsentation und Projektvorschlag
```
