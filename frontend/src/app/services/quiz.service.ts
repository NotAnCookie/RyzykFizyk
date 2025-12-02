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
  private baseUrl = 'http://localhost:8000/api/questions';

  getQuiz(categoryId: string, lang: 'en' | 'pl' = 'en'): Observable<QuestionResponse[]> {
    const url = `${this.baseUrl}?category=${categoryId}&lang=${lang}&amount=7`;
    return this.http.get<QuestionResponse[]>(url);
  }

  getCategories(): Observable<CategoryResponse[]>{
  const url = `${this.baseUrl}/categories`;
    return this.http.get<CategoryResponse[]>(url);
  }
}
