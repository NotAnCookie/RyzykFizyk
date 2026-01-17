import { Injectable, signal } from '@angular/core';

export type Theme = 'light' | 'dark';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private currentTheme = signal<Theme>(this.loadTheme());

  constructor() {
    this.applyTheme(this.currentTheme());
  }

  getCurrentTheme() {
    return this.currentTheme;
  }

  setTheme(theme: Theme) {
    this.currentTheme.set(theme);
    this.saveTheme(theme);
    this.applyTheme(theme);
  }

  toggleTheme() {
    const newTheme = this.currentTheme() === 'light' ? 'dark' : 'light';
    this.setTheme(newTheme);
  }

  private applyTheme(theme: Theme) {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }

  private loadTheme(): Theme {
    const savedTheme = localStorage.getItem('theme');
    return (savedTheme as Theme) || 'light';
  }

  private saveTheme(theme: Theme) {
    localStorage.setItem('theme', theme);
  }
}