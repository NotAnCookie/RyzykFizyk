import { Component, EventEmitter, inject, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LanguageService } from '../services/language.service';

@Component({
  selector: 'app-loading-screen',
  imports: [],
  templateUrl: './loading-screen.component.html',
  styleUrl: './loading-screen.component.css'
})
export class LoadingScreenComponent {

  protected languageService = inject(LanguageService);

  @Output() cancel = new EventEmitter<void>();

}
