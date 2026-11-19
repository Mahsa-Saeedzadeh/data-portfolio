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
- Random Forest erreicht auf KU-HAR nahezu 100 % Accuracy. Die 24 statistischen
  Features reichen für die stark vorverarbeiteten Laborfenster aus.
- Auf HAR70+ werden Alltagsaktivitäten (Gehen, Sitzen, Liegen) gut erkannt,
  Übergänge seltener. Die wichtigsten Features stammen vom Oberschenkelsensor.
- Ältere Probanden zeigen deutlich geringere Varianz und Energie der
  Bewegungen.

## Ausführen

```bash
pip install -r requirements.txt
# Daten gemäß data/README.md ablegen
jupyter notebook notebooks/har_analysis.ipynb
```

Python 3.12, pandas, NumPy, scikit-learn, matplotlib, seaborn.

## Struktur

```text
notebooks/har_analysis.ipynb   Analyse mit Erläuterungen und Ergebnissen
data/                          Download-Anleitung und Datensatzbeschreibung
docs/                          Präsentation und Projektvorschlag
```
