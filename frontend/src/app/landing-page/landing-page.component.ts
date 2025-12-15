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
import { producerUpdatesAllowed } from '@angular/core/primitives/signals';

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
  sessionID: number|null = null;
  answerData: any = null;

  ngOnInit(): void {
    this.loadCategories();
  }

  loadCategories() {
    this.quizService.getCategories().subscribe({
    next: (data: any[]) => { // Używamy any[], żeby TypeScript nie krzyczał przy naprawianiu
        
        console.log("Surowe dane z Pythona:", data);

        let cleanCategories: CategoryResponse[] = [];

        if (data.length > 0 && !data[0].name) {
          console.warn("Wykryto zagnieżdżone dane! Uruchamiam naprawę...");
          
          const rawObject = data[0]; 
          
          cleanCategories = Object.keys(rawObject).map(key => {
             return {
               id: key,                 
               name: rawObject[key].name 
             };
          });

        } else {
          cleanCategories = data;
        }
        /*this.categories = [
          { id: 'random', name: 'Random 🎲' },
          ...cleanCategories
        ];*/
        this.categories = cleanCategories;

        if (this.categories.length > 0) {
          this.selectedCategory = this.categories[0].id;
        }

      },
      error: (err) => {
        //console.error("Błąd pobierania kategorii:", err);
        this.categories = [{ id: 'error', name: 'Błąd połączenia' }];
       // this.categories.unshift({ id: 'x', name: 'Random 🎲' });  
        this.selectedCategory = this.categories[0].id;

      }
    });
  }

startGame() {
    if (!this.selectedCategory) {
      alert("Wybierz kategorię!");
      return;
    }

    this.questionsList = [];     
    this.currentQuestion = null;
    this.currentQuestionIndex = 0;
    this.showGameSummary = false;    
    this.showQuestionCard = false; 

    this.showQuestionCard = true;

  this.quizService.createSession("Player1", this.selectedCategory, 'en').subscribe({
    next: (response: any) => {

      this.questionsList = [response.current_question]; 
      this.currentQuestion = response.current_question;
      this.currentQuestionIndex = 0;
      this.showQuestionCard = true; 
      this.sessionID = response.session_id;

      if(this.sessionID){
        this.loadQuestions(this.sessionID, 6);
      }
    },
    error: (err) => {
      console.error("Błąd startu:", err);
      // Fallback do mocków (opcjonalnie)
      //this.questionsList = this.getMockQuestions();
      if(this.questionsList.length > 0) {
          this.currentQuestion = this.questionsList[0];
          this.currentQuestionIndex = 0;
          this.showQuestionCard = true;
      }
    }
  });
  }


  loadQuestions(sessionId: number, count: number) {
    for (let i = 0; i < count; i++) {
      this.quizService.generateBackgroundQuestion(sessionId).subscribe({
        next: (nextQ) => {
          this.questionsList.push(nextQ);
        },
        error: (e) => console.error("Błąd tła:", e)
      });
    }
  }

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

  getRandomCategory(): CategoryResponse{
    
    const randomIndex = Math.floor(Math.random()*this.categories.length);
    return this.categories[randomIndex];
  }

  showAnswer() {
    this.quizService.verifyAnswer(this.currentQuestion!.id, 111)
      .subscribe({
        next: (updatedQuestion) => {

            if (this.questionsList[this.currentQuestionIndex]) {
               this.questionsList[this.currentQuestionIndex] = updatedQuestion;
            }
            this.currentQuestion = updatedQuestion;

           this.answerData = {
               question: updatedQuestion.text,
               correctAnswer: updatedQuestion.answer, 
               userAnswer: 111,
               source: updatedQuestion.sourceUrl,
               trivia: updatedQuestion.trivia
           };
           this.showAnswerCard = true;
        },
        error: (err) => console.error("Błąd weryfikacji:", err)
      });
}


  handleNextQuestion() {
    if (this.currentQuestionIndex >= 6) { 
       this.finishGame();
       return;
    }
    this.quizService.getNextQuestion().subscribe({
      next: (nextQuestionFromBackend) => {
        console.log("⏩ Backend potwierdził zmianę. Nowe pytanie:", nextQuestionFromBackend);

        this.currentQuestionIndex++;
        
        this.currentQuestion = nextQuestionFromBackend;
        if (!this.questionsList[this.currentQuestionIndex]) {
           this.questionsList.push(nextQuestionFromBackend);
        } else {
           this.questionsList[this.currentQuestionIndex] = nextQuestionFromBackend;
        }

        this.showAnswerCard = false;
        this.showQuestionCard = true;
      },
      error: (err) => {
        console.error("Błąd przesuwania pytania:", err);

      }
    });
  }

  finishGame()
  {
    this.showQuestionCard = false;
    this.showAnswerCard = false;
    this.showGameSummary = true;
    this.quizService.endSession().subscribe(); 

  }

  backToMenu() {
  this.quizService.endSession().subscribe(); 

  this.showGameSummary = false;
  this.showQuestionCard = false;
  this.showAnswerCard = false;
  this.questionsList = []; 
  this.currentQuestionIndex = 0;
  this.selectedCategory = ""; 
  }

  // Zwraca listę pytań awaryjnych (gdy backend nie działa)
 /* getMockQuestions(): QuestionResponse[] {
    return [
      {
        id: 1,
        category: 'Demo',
        topic: 'Angular',
        text: 'Angular jest frameworkiem stworzonym przez firmę [???].',
        answer: 'Google',
        language: 'pl'
      },
      {
        id: 2,
        category: 'Demo',
        topic: 'Układ Słoneczny',
        text: 'Największą planetą w Układzie Słonecznym jest [???].',
        answer: 'Jowisz',
        language: 'pl'
      },
      {
        id: 3,
        category: 'Demo',
        topic: 'Matematyka',
        text: 'Liczba Pi w przybliżeniu wynosi 3,[???].',
        answer: '14',
        language: 'pl'
      },
      {
        id: 4,
        category: 'Demo',
        topic: 'Historia Polski',
        text: 'Chrzest Polski odbył się w roku [???].',
        answer: '966',
        language: 'pl'
      },
      {
        id: 5,
        category: 'Demo',
        topic: 'Chemia',
        text: 'Symbol chemiczny złota to [???].',
        answer: 'Au',
        language: 'pl'
      },
      {
        id: 6,
        category: 'Demo',
        topic: 'Biologia',
        text: 'Dorosły człowiek ma zazwyczaj [???] zęby (wliczając ósemki).',
        answer: '32',
        language: 'pl'
      },
      {
        id: 7,
        category: 'Demo',
        topic: 'Geografia',
        text: 'Stolicą Francji jest [???].',
        answer: 'Paryż',
        language: 'pl'
      }
    ];
  }*/
}