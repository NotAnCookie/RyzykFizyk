import { Component } from '@angular/core';
import { CommonModule } from '@angular/common'; 
import { FormsModule } from '@angular/forms'; 

@Component({
  selector: 'app-landing-page',
  standalone: true, 
  imports: [
    CommonModule, 
    FormsModule  
  ],
  templateUrl: './landing-page.component.html',
  styleUrl: './landing-page.component.css'
})
export class LandingPageComponent {
  
  isProfileOpen: boolean = false;
  isSettingsOpen: boolean = false;
  

  selectedCategory: string = ''; 

  showTriviaQuestion: boolean = false;

  categories = [
    { id: 'cat_1', name: 'Mechanika Klasyczna' },
    { id: 'cat_2', name: 'Termodynamika' },
    { id: 'cat_3', name: 'Elektromagnetyzm' },
    { id: 'cat_4', name: 'Fizyka Kwantowa' }
  ];

  startGame() {
    this.showTriviaQuestion = true;
    console.log('Rozpoczynanie gry z kategorią:', this.selectedCategory);
  }

  openProfile() {
    this.isProfileOpen = true;
  }

  openSettings() {
    this.isSettingsOpen = true;
  }
}