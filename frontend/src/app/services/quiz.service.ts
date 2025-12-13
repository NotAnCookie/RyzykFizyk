import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { QuestionResponse } from '../models/question.model';

export interface CategoryResponse{
  id: string;
  name: string;
}

@Injectable({
  providedIn: 'root'
})

export class QuizService {

  private http = inject(HttpClient);
  
  // Adres do Twojego routera questions
  private baseUrl = 'http://localhost:8000/api/questions';

  // 1. Pobieranie pytań (Quiz)
  getQuiz(categoryId: string, lang: 'en' | 'pl' = 'en'): Observable<QuestionResponse[]> {
    // Ważne: dokleja "/generate-quiz"
    const url = `${this.baseUrl}/generate-quiz?category=${categoryId}&lang=${lang}&amount=7`;
    return this.http.get<QuestionResponse[]>(url);
  }

  // 2. Pobieranie kategorii
  getCategories(): Observable<CategoryResponse[]> {
    // Ważne: dokleja "/categories"
    const url = `${this.baseUrl}/categories`;
    return this.http.get<CategoryResponse[]>(url);
  }
}
