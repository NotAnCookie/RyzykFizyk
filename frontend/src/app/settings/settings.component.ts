import { Component, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

// to do usunięcia później!!!!!!!!!!!!!!!
type LanguageCode = 'en'|'pl';

interface Language {
  code: LanguageCode;
  name: string;
  flag: string;
}

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './settings.component.html',
  styleUrl: './settings.component.css'
})
export class SettingsComponent {

  selectedLanguage: LanguageCode = 'en';

  languages: Language[] = 
  [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'pl', name: 'Polish', flag: '🇵🇱' },
  ];

  selectLanguage(code: LanguageCode)
  {
    this.selectedLanguage = code;
  }

  @Output() close = new EventEmitter<void>();

  handleClose()
  {
    this.close.emit();
  }
}
