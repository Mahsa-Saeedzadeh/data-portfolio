"""
Sprachenspiel

Ein Wort-Erratenspiel mit mehreren Sprachen.
Der Spieler wählt eine Sprache und Schwierigkeit und versucht,
ein zufälliges Wort zu erraten.

Die Wörter werden aus externen Textdateien geladen.
"""

import random
import os


def load_words(language, difficulty):
    """
    Lädt Wörter aus einer Datei basierend auf Sprache und Schwierigkeit.

    :param language: Sprachkürzel (z. B. 'de', 'en', 'it', 'es')
    :param difficulty: Schwierigkeitsgrad ('leicht', 'mittel', 'schwer')
    :return: Liste von Wörtern

    :raises FileNotFoundError: Wenn die Wortdatei nicht existiert
    :raises ValueError: Wenn die Wortliste leer ist
    """

    # Pfad zur aktuellen Datei (wichtig für stabile Dateizugriffe). Finde den Ordner, in dem diese Python-Datei liegt
    base_path = os.path.dirname(__file__)

    # Zusammensetzen des Dateinamens. Baue den kompletten Pfad zur Datei
    filename = os.path.join(base_path, "words", f"{language}_{difficulty}.txt")

    # Prüfen, ob Datei existiert. Sorgt dafür, dass der Pfad auf Windows / Mac / Linux funktioniert
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Wortliste nicht gefunden: {filename}")

    # Datei öffnen und Wörter einlesen
    with open(filename, "r", encoding="utf-8") as file:
        # Entferne Leerzeichen und Zeilenumbrüche. Nur Zeilen behalten, die nicht leer sind
        words = [line.strip() for line in file if line.strip()]

    # Prüfen, ob Liste leer ist
    if not words:
        raise ValueError("Die Wortliste ist leer!")

    return words


class Sprachenspiel:
    """
    Klasse für die Spiellogik des Wortspiels.
    """

    def __init__(self, language="de", difficulty="mittel"):
        """
        Konstruktor: Initialisiert das Spiel

        :param language: gewählte Sprache
        :param difficulty: gewählter Schwierigkeitsgrad
        """

        # Maximale Fehlversuche je Schwierigkeit
        self.max_attempts = {
            "leicht": 10,
            "mittel": 7,
            "schwer": 5
        }

        # Wörter aus externer Datei laden
        words = load_words(language, difficulty)

        # Attribute speichern
        self.language = language
        self.difficulty = difficulty

        # Zufälliges Wort auswählen
        self.word = random.choice(words)

        # Liste für bereits geratene Buchstaben
        self.guessed_letters = []

        # Verbleibende Versuche
        self.remaining_attempts = self.max_attempts[difficulty]

    def display_word(self):
        """
        Gibt das Wort mit Platzhaltern (_) zurück.

        Bereits erratene Buchstaben werden angezeigt.
        """

        display = ""

        # Durch jeden Buchstaben im Wort iterieren
        for letter in self.word:

            # Wenn Buchstabe erraten wurde → anzeigen
            if letter in self.guessed_letters:
                display += letter + " "
            else:
                display += "_ "

        return display.strip()

    def guess_letter(self, letter):
        """
        Verarbeitet einen geratenen Buchstaben.

        :param letter: eingegebener Buchstabe
        """

        # Prüfen, ob Buchstabe schon geraten wurde
        if letter in self.guessed_letters:
            print("⚠️ Dieser Buchstabe wurde bereits geraten.")
            return

        # Buchstabe zur Liste hinzufügen
        self.guessed_letters.append(letter)

        # Prüfen, ob Buchstabe im Wort enthalten ist
        if letter not in self.word:
            self.remaining_attempts -= 1
            print("❌ Falsch geraten!")

    def is_won(self):
        """
        Prüft, ob alle Buchstaben erraten wurden.

        :return: True wenn gewonnen, sonst False
        """

        # all() prüft, ob ALLE Buchstaben erraten wurden
        return all(letter in self.guessed_letters for letter in self.word)

    def is_lost(self):
        """
        Prüft, ob keine Versuche mehr übrig sind.

        :return: True wenn verloren, sonst False
        """

        return self.remaining_attempts <= 0


def choose_language():
    """
    Fragt den Benutzer nach der gewünschten Sprache.

    :return: gültige Sprache
    """

    while True:
        lang = input("Sprache wählen (de/en/it/es): ").lower()

        if lang in ["de", "en", "it", "es"]:
            return lang
        else:
            print("❌ Ungültige Sprache!")


def choose_difficulty():
    """
    Fragt den Benutzer nach dem Schwierigkeitsgrad.

    :return: gültige Schwierigkeit
    """

    while True:
        diff = input("Schwierigkeit (leicht/mittel/schwer): ").lower()

        if diff in ["leicht", "mittel", "schwer"]:
            return diff
        else:
            print("❌ Ungültige Eingabe!")


def get_letter_input():
    """
    Holt eine gültige Eingabe (ein Buchstabe).

    :return: gültiger Buchstabe
    """

    while True:
        letter = input("Rate einen Buchstaben: ").lower()

        # Validierung der Eingabe
        if len(letter) == 1 and letter.isalpha():
            return letter
        else:
            print("❌ Bitte genau einen Buchstaben eingeben!")


def main():
    """
    Hauptfunktion: steuert den gesamten Spielablauf
    """

    print("=== 🌍🌍🌍 Sprachenspiel 🌍🌍🌍 ===")

    # Auswahl von Sprache und Schwierigkeit
    language = choose_language()
    difficulty = choose_difficulty()

    # Exception Handling beim Erstellen des Spiels
    try:
        game = Sprachenspiel(language, difficulty)
    except (FileNotFoundError, ValueError) as e:
        print("Fehler:", e)
        return

    # Hauptspiel-Schleife
    while not game.is_won() and not game.is_lost():
        print("\nWort:", game.display_word())
        print("Verbleibende Versuche:", game.remaining_attempts)
        print("Geratene Buchstaben:", game.guessed_letters)

        # Eingabe holen
        letter = get_letter_input()

        # Eingabe verarbeiten
        game.guess_letter(letter)

    # Spielende
    if game.is_won():
        print("\n🎉 Du hast gewonnen!")
    else:
        print("\n💀 Du hast verloren!")

    print("Das Wort war:", game.word)


# Startpunkt des Programms, wenn diese Datei direkt gestartet wird
if __name__ == "__main__":
    main()
