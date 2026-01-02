import { Component, Output,Input, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; 
import { QuestionResponse } from "../models/question.model";
import { LanguageService } from '../services/language.service';

@Component({
  selector: 'app-question-answer-card',
  standalone: true,
  imports: [CommonModule, FormsModule], 
  templateUrl: './question-answer-card.component.html',
  styleUrl: './question-answer-card.component.css'
})
export class QuestionAnswerCardComponent {

  protected languageService = inject(LanguageService);
  @Input() question!: QuestionResponse;

  @Output() back = new EventEmitter<void>();
  @Output() next = new EventEmitter<void>();

  @Input() currentQuestionIndex: number = 0;
  @Input() totalQuestions: number = 0;

  handleBack() 
  {
    this.back.emit();
  }

  handleNext()
  {
    this.next.emit();
  }
}