import { Component, Output, Input, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; 
import { QuestionResponse } from "../models/question.model";
import { LanguageService } from '../services/language.service';

@Component({
  selector: 'app-question-card',
  standalone: true,
  imports: [CommonModule, FormsModule], 
  templateUrl: './question-card.component.html',
  styleUrl: './question-card.component.css'
})
export class QuestionCardComponent {
  protected languageService = inject(LanguageService);

  @Input() question!: QuestionResponse;
  @Input() currentQuestionIndex: number = 0;
  @Input() totalQuestions: number = 0;

  @Output() back = new EventEmitter<void>();
  @Output() next = new EventEmitter<void>();

  handleBack() 
  {
    this.back.emit();
  }

  handleNext()
  {
    this.next.emit();
  }
}