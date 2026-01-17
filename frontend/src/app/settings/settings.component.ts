import { Component, Output, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LanguageService, LanguageCode } from '../services/language.service';
import { ThemeService } from '../services/theme.service';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.css'
})
export class SettingsComponent {

  protected languageService = inject(LanguageService);
  protected themeService = inject(ThemeService);

  @Output() close = new EventEmitter<void>();

  get currentTheme() {
    return this.themeService.getCurrentTheme();
  }

  selectLanguage(code: LanguageCode)
  {
    this.languageService.setLanguage(code);
  }

  selectTheme(theme: 'light' | 'dark') {
    this.themeService.setTheme(theme);
  }

  handleClose()
  {
    this.close.emit();
  }
}
