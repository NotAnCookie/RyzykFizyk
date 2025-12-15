import { Component, EventEmitter, Output, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { QuestionResponse } from "../models/question.model";


@Component({
  selector: 'app-game-summary',
  standalone: true,
  imports: [CommonModule], // Kluczowe dla *ngFor
  templateUrl: './game-summary.component.html',
  styleUrl: './game-summary.component.css'
})
export class GameSummaryComponent {
  @Input() questions: QuestionResponse[] = [];

  @Output() back = new EventEmitter<void>();
  @Output() playAgain = new EventEmitter<void>();

  // przykładowe dane!!!!
  /*questions = [
    {
      id: 1,
      question: "How many countries are there in the world?",
      correctAnswer: "195"
    },
    {
      id: 2,
      question: "What year was the first iPhone released?",
      correctAnswer: "2007"
    },
    {
      id: 3,
      question: "How many keys does a standard piano have?",
      correctAnswer: "88"
    },
    {
      id: 4,
      question: "How many bones are in the adult human body?",
      correctAnswer: "206"
    },
    {
      id: 5,
      question: "What is the height of Mount Everest in meters?",
      correctAnswer: "8849"
    },
    {
      id: 6,
      question: "How many stripes are on the American flag?",
      correctAnswer: "13"
    },
    {
      id: 7,
      question: "What is the speed of light in km/s (rounded)?",
      correctAnswer: "300000"
    }
  ];*/

  handleBack() {
    this.back.emit();
  }

  handlePlayAgain() {
    this.playAgain.emit();
  }
}