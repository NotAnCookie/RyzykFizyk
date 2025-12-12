import { Component, Output,Input, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms'; 
import { QuestionResponse } from "../models/question.model";

@Component({
  selector: 'app-question-answer-card',
  standalone: true,
  imports: [CommonModule, FormsModule], 
  templateUrl: './question-answer-card.component.html',
  styleUrl: './question-answer-card.component.css'
})
export class QuestionAnswerCardComponent {

  @Input() question!: QuestionResponse;

  @Output() back = new EventEmitter<void>();
  @Output() next = new EventEmitter<void>();

  // Na razie jakiekolwiek pytanie
@Input() answerData = {
    question: "How tall is the Eiffel Tower?",
    category: "Geography",
    correctAnswer: "330 meters (1,083 feet)",
    userAnswer: "300 meters",    funFact: "The Eiffel Tower can be 15 cm taller during the summer due to thermal expansion of the iron structure when heated by the sun.",
    source: "https://www.toureiffel.paris",
    sourceDisplay: "toureiffel.paris"
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