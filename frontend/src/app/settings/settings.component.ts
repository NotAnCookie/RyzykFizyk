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

  selectLanguage(code: LanguageCode)
  {
    this.languageService.setLanguage(code);
  }

  handleClose()
  {
    this.close.emit();
  }
}
