import random
import os
from services.question_generator.src.enums import Language
from questions_generator import generate_question

# Importujemy listę kategorii z Twojego pliku config
# import z categories instead
try:
    from categories import AVAILABLE_CATEGORIES
except ImportError:
    # Fallback, gdyby import się nie udał (dla bezpieczeństwa)
    print("Błąd: Nie znaleziono pliku config.py lub listy AVAILABLE_CATEGORIES.")
    exit()

def clear_screen():
    """Czyści ekran terminala (działa na Windows i Linux/Mac)."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear_screen()
    print("==========================================")
    print("   GENERATOR PYTAŃ Z WIKIPEDII")
    print("==========================================\n")
    print(f"Wczytano {len(AVAILABLE_CATEGORIES)} kategorii z pliku config.")
    
    while True:
        print("\n" + " Naciśnij [ENTER], aby wylosować pytanie ".center(42, "-"))
        print(" (wpisz 'q' lub 'exit' aby zakończyć)")
        
        user_input = input(">> ")
        
        if user_input.lower() in ['q', 'exit']:
            print("Do zobaczenia!")
            break
            
        # 1. Losujemy kategorię z konfiguracji
        selected_category = random.choice(AVAILABLE_CATEGORIES)
        
        print(f"\n🔍 Szukam ciekawostki w kategorii: {selected_category.name}...")
        
        # 2. Generujemy pytanie
        question = generate_question(
            category=selected_category, 
            language=Language.ENG  # Możesz zmienić na Language.PL
        )
        
        # 3. Wyświetlanie wyniku
        if question:
            print("\n" + " PYTANIE ".center(40, "="))
            print(f"TEMAT: {question.topic}")
            print(f"TREŚĆ: {question.question_text}")
            print("-" * 40)
            
        else:
            print("\n❌ Nie udało się znaleźć pytania w tej próbie. Spróbuj ponownie.")

if __name__ == "__main__":
    main()