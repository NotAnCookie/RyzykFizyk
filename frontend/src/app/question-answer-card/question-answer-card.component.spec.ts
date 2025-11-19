import { ComponentFixture, TestBed } from '@angular/core/testing';

import { QuestionAnswerCardComponent } from './question-answer-card.component';

describe('QuestionAnswerCardComponent', () => {
  let component: QuestionAnswerCardComponent;
  let fixture: ComponentFixture<QuestionAnswerCardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [QuestionAnswerCardComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(QuestionAnswerCardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
