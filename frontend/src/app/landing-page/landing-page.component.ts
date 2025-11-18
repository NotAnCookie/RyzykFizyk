import { Component } from '@angular/core';
import { CommonModule } from '@angular/common'; // Potrzebne dla *ngIf i *ngFor
import { FormsModule } from '@angular/forms'; // Potrzebne dla [(ngModel)]

@Component({
  selector: 'app-landing-page',
  standalone: true, // Nowoczesne komponenty Angulara są domyślnie 'standalone'
  imports: [
    CommonModule, // Importujemy CommonModule
    FormsModule   // Importujemy FormsModule
  ],
  templateUrl: './landing-page.component.html',
  styleUrl: './landing-page.component.css'
})
export class LandingPageComponent {

  // --- To zastępuje `useState` z Reacta ---
  
  // Stan dla wysuwanych paneli
  isProfileOpen: boolean = false;
  isSettingsOpen: boolean = false;
  
  // Stan dla wybranej kategorii
  // Zaczynamy od pustego stringa, żeby nic nie było domyślnie zaznaczone
  selectedCategory: string = ''; 

  // Stan do pokazania pytania (po kliknięciu "Start Game")
  showTriviaQuestion: boolean = false;

  // Mock-data (dane zastępcze) dla kategorii
  // W prawdziwej aplikacji przyszłyby one z backendu
  categories = [
    { id: 'cat_1', name: 'Mechanika Klasyczna' },
    { id: 'cat_2', name: 'Termodynamika' },
    { id: 'cat_3', name: 'Elektromagnetyzm' },
    { id: 'cat_4', name: 'Fizyka Kwantowa' }
  ];

  // --- To są nasze "event handlery" ---

  // Metoda wywoływana przez przycisk "Start Game"
  startGame() {
    // Na razie po prostu zmieniamy stan
    // W przyszłości mogłoby to np. nawigować do innej podstrony
    this.showTriviaQuestion = true;
    console.log('Rozpoczynanie gry z kategorią:', this.selectedCategory);
    // Tutaj możesz dodać logikę nawigacji, np. this.router.navigate(['/quiz']);
  }

  // Metody do otwierania paneli (dla przejrzystości)
  // Chociaż w Angularze możemy to zrobić też prosto w HTMLu
  openProfile() {
    this.isProfileOpen = true;
  }

  openSettings() {
    this.isSettingsOpen = true;
  }
}