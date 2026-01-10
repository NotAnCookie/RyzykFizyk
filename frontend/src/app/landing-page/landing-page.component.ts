import { Component, inject, OnInit, effect, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common'; 
import { FormsModule } from '@angular/forms'; 
import { SettingsComponent } from '../settings/settings.component';
//import { UserProfileComponent } from '../user-profile/user-profile.component';
import { QuestionCardComponent } from '../question-card/question-card.component';
import { QuestionAnswerCardComponent } from '../question-answer-card/question-answer-card.component';
import { GameSummaryComponent } from '../game-summary/game-summary.component';
import { QuizService, CategoryResponse } from '../services/quiz.service';
import { QuestionResponse } from '../models/question.model';
// removed unused import
import { LanguageService } from '../services/language.service';
import { LoadingScreenComponent } from '../loading-screen/loading-screen.component';
import { ConfirmationPopUpComponent } from '../confirmation-pop-up/confirmation-pop-up.component';
import { Subscription } from 'rxjs';

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
    GameSummaryComponent,
    LoadingScreenComponent,
    ConfirmationPopUpComponent,
  ],
  templateUrl: './landing-page.component.html',
  styleUrls: ['./landing-page.component.css']
})
export class LandingPageComponent implements OnInit {
  
  private quizService = inject(QuizService);
  public languageService = inject(LanguageService);

  isGameActive: boolean = false; 
  private backgroundSub: Subscription | null = null;

  //isProfileOpen: boolean = false;
  isSettingsOpen: boolean = false;
  
  isLoading: boolean = false;
  showExitConfirmation: boolean = false;
  showError: boolean = false;
  errorMessage: string = this.languageService.t().connectionError;
  
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

  constructor() {
    effect(() => {
      const lang = this.languageService.currentLang();
      
      console.log('🔄 Wykryto zmianę języka na:', lang, '- pobieram nowe kategorie...');
      
      this.loadCategories();
    });
  }

  ngOnInit(): void {
    this.loadCategories();
  }

  loadCategories() {
    this.quizService.getCategories(this.languageService.currentLang()).subscribe({
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
        console.error("Błąd pobierania kategorii:", err);
        this.categories = [{ id: 'error', name: this.languageService.t().connectionError }];
        this.selectedCategory = this.categories[0].id;

      }
    });
  }

startGame() {
    if (!this.selectedCategory) {
      alert("Wybierz kategorię!");
      return;
    }
    
    this.isGameActive = true;

    this.questionsList = [];     
    this.currentQuestion = null;
    this.currentQuestionIndex = 0;
    this.showGameSummary = false;    
    this.showQuestionCard = false; 
    this.isLoading = true;
    this.showError = false;

  this.quizService.createSession("Player1", this.selectedCategory, this.languageService.currentLang()).subscribe({
    next: (response: any) => {

      if(!this.isGameActive){
        this.exitGame();
        return;
      }

        const rawQuestion = response.current_question;
        this.sessionID = response.session_id;

        console.log("✅ Sesja utworzona. Pytanie 1 (z metadanymi):", rawQuestion);
        
        this.handleFirstQuestion(rawQuestion);
    },
    error: (err) => {
      console.error("Błąd startu:", err);

        this.isLoading = false; 
        this.isGameActive = false;
        
        this.errorMessage = this.languageService.currentLang() === 'pl' 
            ? "Nie udało się połączyć z serwerem gry. Spróbuj ponownie." 
            : "Could not connect to game server. Please try again.";
            
        this.showError = true;

      if(this.questionsList.length > 0) {
          this.currentQuestion = this.questionsList[0];
          this.currentQuestionIndex = 0;
          this.showQuestionCard = true;
      }
    }
  });
  }

  handleFirstQuestion(question: QuestionResponse) {
    if(!this.isGameActive){ this.exitGame(); return; }

    this.questionsList = [question];
    this.currentQuestion = question;
    
    this.showQuestionCard = true;
    this.isLoading = false; 

    // if (this.sessionID) {
    //     this.loadQuestions(this.sessionID, 6);
    // }
}

  loadQuestions(sessionId: number, count: number, currentCount: number = 0) {
    if(!this.isGameActive) return;

    if(this.questionsList.length >= count) return;

    if(currentCount >= 20) return;

    this.backgroundSub = this.quizService.generateBackgroundQuestion(sessionId).subscribe({
          next: (nextQ) => {
            console.log(`📥 Pytanie tła #${currentCount + 1} gotowe:`, nextQ.text?.substring(0, 20) + "...");

            if(!this.isGameActive) return;
            
            this.quizService.verifyAnswer(nextQ.id, 111).subscribe({

                next: (verifiedNextQ) => {
                    console.log(`📥 Pytanie tła #${currentCount + 1} gotowe i zweryfikowane.`);

                    if(!this.isGameActive) return;
                    
                    this.questionsList.push(verifiedNextQ);
                    this.loadQuestions(sessionId, count, currentCount + 1);
                },
                error: (err) => {
                    if (!this.isGameActive) return;
                    console.error("Błąd weryfikacji w tle:", err);

                    const fallbackQ: QuestionResponse = {
                        ...nextQ, 
                        sourceUrl: "null", 
                        trivia: "null"
                    };

                    this.questionsList.push(fallbackQ);
                    this.loadQuestions(sessionId, count, currentCount + 1);
                }
            });
          },
          error: (e) => {
            if (!this.isGameActive) return;
            console.error(`❌ Generating question error #${currentCount + 1}:`, e);
            this.loadQuestions(sessionId, count, currentCount + 1);
          }
        });
  }

  getCategoryName(id: string): string {
    if (!this.categories || this.categories.length === 0) return id;

    const foundCategory = this.categories.find(c => c.id === id);

    return foundCategory ? foundCategory.name : id;
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
    const currQ = this.currentQuestion;
    if(!currQ) return;

    this.answerData = {
      question: currQ.text,
      correctAnswer: currQ.answer, 
      userAnswer: 111,
      source: currQ.sourceUrl,
      trivia: currQ.trivia
      };

    this.showAnswerCard = true;
    this.showQuestionCard=false;

}

handleNextQuestion() {
    // 1. Sprawdzenie końca gry
    if (this.currentQuestionIndex >= 6) { 
       this.finishGame();
       return;
    }

    this.isLoading = true; 

    const nextIndex = this.currentQuestionIndex + 1;

    if (this.questionsList.length > nextIndex && this.questionsList[nextIndex]) {
        console.log("⏩ [Frontend] Używam pytania z cache (załadowanego w tle).");
        this.advanceToQuestion(this.questionsList[nextIndex]);
        return;
    } 

    console.log("⏳ [Frontend] Brak pytania w cache. Pytam backend...");
    
    this.quizService.getNextQuestion().subscribe({
      next: (nextQuestionFromBackend) => {
        console.log("⏩ [Frontend] Pytanie pobrane z serwera:", nextQuestionFromBackend);
        this.questionsList.push(nextQuestionFromBackend);
        this.advanceToQuestion(nextQuestionFromBackend);
      },
      error: (err) => {
        console.error("❌ [Frontend] Błąd pobierania nextQuestion:", err);
        this.isLoading = false;
        
        this.errorMessage = this.languageService.currentLang() === 'pl' 
            ? "Nie udało się pobrać kolejnego pytania." 
            : "Could not retrieve the next question.";
        this.showError = true;
      }
    });
  }

  private advanceToQuestion(question: QuestionResponse) {
      this.currentQuestionIndex++;
      this.currentQuestion = question;
      
      this.showAnswerCard = false;
      this.showQuestionCard = true;
      
      this.isLoading = false; // Wyłączamy loader dopiero gdy wszystko gotowe
  }
  
  finishGame()
  {
    this.showQuestionCard = false;
    this.showAnswerCard = false;
    this.showGameSummary = true;
    this.quizService.endSession().subscribe(); 
  }

  exitGame() {

    this.isGameActive = false;
    this.showExitConfirmation = false;

    if (this.backgroundSub) {
        this.backgroundSub.unsubscribe();
        this.backgroundSub = null;
    }

    if (this.sessionID) {
        this.quizService.endSession().subscribe();
    }

  this.showGameSummary = false;
  this.showQuestionCard = false;
  this.showAnswerCard = false;
  this.questionsList = []; 
  this.currentQuestionIndex = 0;
  this.selectedCategory = this.categories[0].id;
  }

  cancelLoading() {
    this.isLoading = false;
    this.exitGame();
}

backToMenu()
{
  this.showExitConfirmation = true;
}

cancelExit()
{
  this.showExitConfirmation = false;
}

  // Handle Tab / Shift+Tab on category buttons: cycle selection and focus among categories only
  handleCategoryTab(event: KeyboardEvent, idx: number) {
    if (event.key !== 'Tab') return;

    event.preventDefault();

    const len = this.categories?.length || 0;
    if (len === 0) return;

    let newIdx: number;
    if (event.shiftKey) {
      newIdx = (idx - 1 + len) % len;
    } else {
      newIdx = (idx + 1) % len;
    }

    this.selectedCategory = this.categories[newIdx].id;

    const el = document.getElementById('category-btn-' + newIdx) as HTMLElement | null;
    el?.focus();
  }

closeErrorModal() {
    this.showError = false;
    this.exitGame(); 
  }

  @HostListener('document:keydown.enter', ['$event'])
  handleEnterKey(event: KeyboardEvent) {
    if (this.showQuestionCard && !this.isLoading) {
     this.showAnswerCard = true;
     this.showQuestionCard = false;
     this.showAnswer();
    }
    else if(this.showAnswerCard && !this.isLoading)
    {
      this.handleNextQuestion();
    }
    else if(this.showGameSummary)
    {
      this.exitGame();
    }
    else if(!this.isGameActive)
    {
      this.startGame();
    }
  }
}