import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// --- INTERFEJSY DANYCH (DTO) ---
// Muszą pasować do tego, czego oczekuje Twój SessionRouter w Pythonie

export interface CreateSessionDTO {
  player_name: string;
  category: string;
  language: string;
}

export interface PlayerAnswerDTO {
  questionId: string;
  value: number; // Backend oczekuje liczby (float)
}

export interface CategoryResponse {
  id: string;
  name: string;
}

@Injectable({
  providedIn: 'root'
})
export class QuizService {
  private http = inject(HttpClient);

  // 1. Adres do SESJI (nowy router)
  private sessionUrl = 'http://localhost:8000/session'; 
  
  // 2. Adres do KATEGORII (stary router, on się nie zmienia)
  private questionsUrl = 'http://localhost:8000/api/questions';

  // --- NOWE METODY SESYJNE (Session Manager) ---

  // KROK 1: Rozpocznij grę
createSession(playerName: string, category: string, lang: string): Observable<any> {
     const body = {
      player_id: 1,                
      player_name: playerName,
      player_email: "guest@example.com", 
      language: lang,
      category: category
    };
    
    return this.http.post(`${this.sessionUrl}/create`, body, { 
      withCredentials: true 
    });
  }

  // KROK 2: Wyślij odpowiedź (Weryfikacja)
  submitAnswer(questionId: string, answerValue: number): Observable<any> {
    const body: PlayerAnswerDTO = {
      questionId: questionId,
      value: answerValue
    };
    return this.http.post(`${this.sessionUrl}/submit_answer`, body, { withCredentials: true });
  }

  // KROK 3: Pobierz kolejne pytanie
  getNextQuestion(): Observable<any> {
    return this.http.post(`${this.sessionUrl}/next_question`, {}, { withCredentials: true });
  }

  generateBackgroundQuestion(sessionId: number): Observable<any> {
    const body = { session_id: sessionId };
    return this.http.post(`${this.sessionUrl}/generate-background`, body, { withCredentials: true });
  }

  verifyAnswer(questionId: string | number, answerValue: number): Observable<any> {
      const body = {
          question_id: questionId,
          value: answerValue
      };
      //return this.http.post(`${this.sessionUrl}/verify_answer`, body, { withCredentials: true });
      return this.http.post(`${this.sessionUrl}/submit_answer`, body, { withCredentials: true });
  }

  // Pomocnicze: Pobierz aktualne pytanie (np. jak odświeżysz stronę)
  getCurrentQuestion(): Observable<any> {
    return this.http.get(`${this.sessionUrl}/current_question`, { withCredentials: true });
  }

  // Pomocnicze: Zakończ grę
  endSession(): Observable<any> {
    return this.http.post(`${this.sessionUrl}/end`, {}, { withCredentials: true });
  }

  //Pobierz kategorie
  getCategories(lang: string): Observable<CategoryResponse[]> {
    const url = `${this.questionsUrl}/categories`;
    return this.http.get<CategoryResponse[]>(url, { params: {lang: lang}});
  }

}