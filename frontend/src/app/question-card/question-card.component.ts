import { Component, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; 

@Component({
  selector: 'app-question-card',
  standalone: true,
  imports: [CommonModule, FormsModule], 
  templateUrl: './question-card.component.html',
  styleUrl: './question-card.component.css'
})
export class QuestionCardComponent {

  @Output() back = new EventEmitter<void>();
  @Output() next = new EventEmitter<void>();

  // Na razie jakiekolwiek pytanie
  question = 
  {
    text: "How tall is the Eiffel Tower?",
    category: "Geography",
  };

  handleBack() 
  {
    this.back.emit();
  }

  handleNext()
  {
    this.next.emit();
  }
}