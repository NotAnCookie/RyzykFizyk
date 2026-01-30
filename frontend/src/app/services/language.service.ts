import { Injectable, signal, computed } from '@angular/core';

export type LanguageCode = 'en' | 'pl';

export interface LanguageOption {
  code: LanguageCode;
  label: string;
  flag: string;
}

export interface Translations {
  startGame: string;
  chooseCategory: string;
  nextQuestion: string;
  showAnswer: string;
  correctAnswer: string;
  showSummary: string;
  funFact: string;
  source: string;
  backToMenu: string;
  loading: string;
  question: string; 
  of: string;
  settings: string;
  close: string;
  gameSummary: string;
  playAgain: string;
  language: string;
  cancel: string;
  sthWentWrong: string;
  connectionError: string;
  theme: string;
  darkMode: string;
  lightMode: string;
  name?: string;
}

@Injectable({
  providedIn: 'root'
})
export class LanguageService {

  public currentLang = signal<LanguageCode>('en');

  public readonly availableLanguages: LanguageOption[] = [
    { code: 'en', label: 'English', flag: '🇬🇧' },
    { code: 'pl', label: 'Polski', flag: '🇵🇱' }
  ];

 private dictionaries: Record<LanguageCode, Translations> = {
  en: {
    startGame: "Start Game",
    chooseCategory: "Choose Category",
    nextQuestion: "Next Question",
    showAnswer: "Show Answer",
    correctAnswer: "Correct Answer",
    showSummary: "Show Summary",
    funFact: "Fun Fact 💡",
    source: "Source",
    backToMenu: "Back to Menu",
    loading: "Generating questions...",
    question: "Question",
    of: "of",
    settings: "Settings",
    close: "Close",
    gameSummary: "Game Summary",
    playAgain: "Play Again",
    language: "Language",
    cancel: "Cancel", 
    sthWentWrong: "Oops, something went wrong...",
    connectionError: "Connection Error",
    theme: "Theme",
    darkMode: "Dark Mode",
    lightMode: "Light Mode",
    name: "Risk Your Knowledge"
  },
  pl: {
    startGame: "Rozpocznij Grę",
    chooseCategory: "Wybierz Kategorię",
    nextQuestion: "Następne Pytanie",
    showAnswer: "Sprawdź Odpowiedź",
    correctAnswer: "Poprawna Odpowiedź",
    showSummary: "Pokaż Podsumowanie",
    funFact: "Ciekawostka 💡",
    source: "Źródło",
    backToMenu: "Powrót do Menu",
    loading: "Generowanie pytań...",
    question: "Pytanie",
    of: "z",
    settings: "Ustawienia",
    close: "Zamknij",
    gameSummary: "Podsumowanie Gry",
    playAgain: "Zagraj Ponownie",
    language: "Język",
    cancel: "Anuluj",
    sthWentWrong: "Ups, coś poszło nie tak...",
    connectionError: "Błąd Połączenia",
    theme: "Motyw",
    darkMode: "Tryb Ciemny",
    lightMode: "Tryb Jasny",
    name: "Zaryzykuj Swoją Wiedzę"
  }
};

  public t = computed(() => this.dictionaries[this.currentLang()]);

  setLanguage(lang: LanguageCode) {
    this.currentLang.set(lang);
  }

  getCurrentLangCode(): LanguageCode {
    return this.currentLang();
  }
}