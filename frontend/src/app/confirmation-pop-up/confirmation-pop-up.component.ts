import { Component, EventEmitter, inject, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LanguageService } from '../services/language.service';
import { ThemeService } from '../services/theme.service';

@Component({
  selector: 'app-confirmation-pop-up',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './confirmation-pop-up.component.html',
  styleUrls: ['./confirmation-pop-up.component.css']
})
export class ConfirmationPopUpComponent {
  
  public languageService = inject(LanguageService);
  public themeService = inject(ThemeService);

  @Output() confirm = new EventEmitter<void>(); // Użytkownik kliknął TAK
  @Output() cancel = new EventEmitter<void>();  // Użytkownik kliknął NIE

  text = {
    pl: {
      title: 'Czy na pewno chcesz wyjść?',
      message: 'To spowoduje zakończenie obecnej sesji gry. Postępy zostaną utracone.',
      yes: 'Tak, wyjdź',
      no: 'Nie, wróć do gry'
    },
    en: {
      title: 'Are you sure you want to exit?',
      message: 'This will end your current game session. Progress will be lost.',
      yes: 'Yes, exit',
      no: 'No, return to game'
    }
  };

  get t() {
    return this.languageService.currentLang() === 'pl' ? this.text.pl : this.text.en;
  }
}