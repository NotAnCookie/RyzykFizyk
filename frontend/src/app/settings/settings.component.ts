import { Component, Output, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LanguageService, LanguageCode } from '../services/language.service'; 

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.css'
})
export class SettingsComponent {

  protected languageService = inject(LanguageService);

  @Output() close = new EventEmitter<void>();

  currentTheme: 'light' | 'dark' = 'light';

  selectLanguage(code: LanguageCode)
  {
    this.languageService.setLanguage(code);
  }

  selectTheme(theme: 'light' | 'dark') {
    this.currentTheme = theme;
    // Here you could add logic to actually apply the theme
  }

  handleClose()
  {
    this.close.emit();
  }
}
