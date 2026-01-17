import { Component, EventEmitter, Output, Input, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { QuestionResponse } from "../models/question.model";
import { LanguageService } from '../services/language.service';
import { ThemeService } from '../services/theme.service';


@Component({
  selector: 'app-game-summary',
  standalone: true,
  imports: [CommonModule], // Kluczowe dla *ngFor
  templateUrl: './game-summary.component.html',
  styleUrl: './game-summary.component.css'
})
export class GameSummaryComponent {
  protected languageService = inject(LanguageService);
  protected themeService = inject(ThemeService);

  @Input() questions: QuestionResponse[] = [];

  @Output() back = new EventEmitter<void>();
  @Output() playAgain = new EventEmitter<void>();

  handleBack() {
    this.back.emit();
  }

  handlePlayAgain() {
    this.playAgain.emit();
  }
}