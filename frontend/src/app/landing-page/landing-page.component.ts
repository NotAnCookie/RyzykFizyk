import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common'; 
import { FormsModule } from '@angular/forms'; 
import { SettingsComponent } from '../settings/settings.component';
//import { UserProfileComponent } from '../user-profile/user-profile.component';
import { QuestionCardComponent } from '../question-card/question-card.component';
import { QuestionAnswerCardComponent } from '../question-answer-card/question-answer-card.component';
import { GameSummaryComponent } from '../game-summary/game-summary.component';
import { QuizService, CategoryResponse } from '../services/quiz.service';
import { QuestionResponse } from '../models/question.model';

@Component({
  selector: 'app-landing-page',
  standalone: true, 
  imports: [
    CommonModule, 
    FormsModule,  
    SettingsComponent,
    //UserProfileComponent
    QuestionCardComponent,
    QuestionAnswerCardComponent,
    GameSummaryComponent
  ],
  templateUrl: './landing-page.component.html',
  styleUrl: './landing-page.component.css'
})
export class LandingPageComponent implements OnInit {
  
  private quizService = inject(QuizService);

  //isProfileOpen: boolean = false;
  isSettingsOpen: boolean = false;
  
  selectedCategory: string = ''; 

  showQuestionCard: boolean = false;
  showAnswerCard:boolean = false;
  showGameSummary:boolean = false;

  categories: CategoryResponse[] = [];

  questionsList: QuestionResponse[] = [];
  currentQuestionIndex: number = 0;
  currentQuestion: QuestionResponse | null = null

  ngOnInit(): void {
    this.loadCategories();
  }

  loadCategories() {
    this.quizService.getCategories().subscribe({
      next: (data) => {
        //console.log("Pobrano kategorie z Pythona:", data);
        this.categories = data;
      },
      error: (err) => {
        //console.error("Błąd pobierania kategorii:", err);
        this.categories = [{ id: 'error', name: 'Błąd połączenia' }];
      }
    });
  }

startGame() {
    if (!this.selectedCategory) {
      alert("Wybierz kategorię!");
      return;
    }

    this.showQuestionCard = true;

    this.quizService.getQuiz(this.selectedCategory).subscribe({
      next: (data) => {
        // SCENARIUSZ POZYTYWNY: Mamy dane z Pythona
        console.log("Pobrano quiz z serwera");
        this.questionsList = data;
        this.finalizeGameStart();
      },
      error: (err) => {
        // SCENARIUSZ NEGATYWNY: Błąd serwera -> Ładujemy Mock Data
        console.warn("Błąd backendu. Ładowanie pytań awaryjnych (offline mode).", err);
        
        this.questionsList = this.getMockQuestions(); // <--- TU JEST KLUCZOWA ZMIANA
        this.finalizeGameStart();
      }
    });
  }

  // Wydzieliłem to do osobnej funkcji, żeby nie powtarzać kodu w 'next' i 'error'
  finalizeGameStart() {
    this.currentQuestionIndex = 0;
    this.loadCurrentQuestion();
  }

  loadCurrentQuestion() {
    if (this.questionsList.length > this.currentQuestionIndex) {
      this.currentQuestion = this.questionsList[this.currentQuestionIndex];
    }
  }

  /*openProfile() {
    this.isProfileOpen = true;
  }*/

  openSettings() {
    this.isSettingsOpen = true;
  }

  // Zwraca listę pytań awaryjnych (gdy backend nie działa)
  getMockQuestions(): QuestionResponse[] {
    return [
      {
        question_id: '1',
        category: 'Demo',
        topic: 'Angular',
        question_text: 'Angular jest frameworkiem stworzonym przez firmę [???].',
        answer: 'Google',
        language: 'pl'
      },
      {
        question_id: '2',
        category: 'Demo',
        topic: 'Układ Słoneczny',
        question_text: 'Największą planetą w Układzie Słonecznym jest [???].',
        answer: 'Jowisz',
        language: 'pl'
      },
      {
        question_id: '3',
        category: 'Demo',
        topic: 'Matematyka',
        question_text: 'Liczba Pi w przybliżeniu wynosi 3,[???].',
        answer: '14',
        language: 'pl'
      },
      {
        question_id: '4',
        category: 'Demo',
        topic: 'Historia Polski',
        question_text: 'Chrzest Polski odbył się w roku [???].',
        answer: '966',
        language: 'pl'
      },
      {
        question_id: '5',
        category: 'Demo',
        topic: 'Chemia',
        question_text: 'Symbol chemiczny złota to [???].',
        answer: 'Au',
        language: 'pl'
      },
      {
        question_id: '6',
        category: 'Demo',
        topic: 'Biologia',
        question_text: 'Dorosły człowiek ma zazwyczaj [???] zęby (wliczając ósemki).',
        answer: '32',
        language: 'pl'
      },
      {
        question_id: '7',
        category: 'Demo',
        topic: 'Geografia',
        question_text: 'Stolicą Francji jest [???].',
        answer: 'Paryż',
        language: 'pl'
      }
    ];
  }
}