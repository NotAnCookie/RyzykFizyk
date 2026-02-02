# Projekt RyzykFizyk

## Tech Stack
<div align="center">
    <code style="margin: 10px;"><img width="75" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/python.png" alt="Python" title="Python"/></code>
    <code style="margin: 10px;"><img width="75" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/react.png" alt="React" title="React"/></code>
    <code style="margin: 10px;"><img width="75" src="https://raw.githubusercontent.com/marwin1991/profile-technology-icons/refs/heads/main/icons/angular.png" alt="Angular" title="Angular"/></code>
</div>



## System Architecture
System oparty jest na architekturze webowej z komunikacją frontend ↔ backend przez **REST API** (HTTP/JSON).  

- **Backend:** Python, wykorzystanie bibliotek AI i integracja z API zewnętrznymi (OpenAI, Wikipedia, Google Custom Search).  
- **Frontend:** JavaScript + React, dynamiczny i responsywny interfejs użytkownika.  
- **Baza danych:** MSSQL  
- **Autoryzacja:** OpenID Connect (logowanie przez Google)  
- **Platforma:** System platformowo niezależny, implementacja i testy prowadzone na Windows.  

## Features
- Generowanie pytań i ciekawostek z zewnętrznych źródeł  
- Integracja z modelami językowymi OpenAI API  

# Instrukcja instalacji
Poniżej opisano proces instalacji i uruchomienia systemu w środowisku lokalnym.

---

## Wymagania wstępne

Do uruchomienia aplikacji wymagane są:

- Python w wersji 3.10 lub nowszej
- Node.js wraz z menedżerem pakietów npm
- Git lub dostęp do archiwum z kodem źródłowym
- aktywne połączenie z Internetem

---

## Backend

### Instalacja

1. Utwórz wirtualne środowisko:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
# source venv/bin/activate
```

2. Zainstaluj zależności:

```bash
pip install -r requirements.txt
```

### Konfiguracja środowiska (.env)

Stwórz plik `.env` w katalogu backendu na podstawie `.env.example` i uzupełnij wymagane klucze API:

- `OPENAI_API_KEY` – Twój klucz API do OpenAI. Pozyskujesz go z [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)
- `GOOGLE_API_KEY` – Klucz API do usług Google (np. wyszukiwarka niestandardowa). Generujesz go w Google Cloud Console.
- `GOOGLE_CX` – Identyfikator własnej wyszukiwarki Google Custom Search Engine (CSE).

Przykład `.env`:

```
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
GOOGLE_CX=0123456789:abcdefg
```

### Uruchomienie backendu

```bash
python -m dotenv run -- uvicorn app.main:app --reload
```

Backend będzie dostępny pod adresem: `http://127.0.0.1:8000`.

---

## Frontend

### Instalacja

W katalogu frontendu:

```bash
npm install
```

### Uruchomienie

```bash
ng serve
```

Frontend będzie dostępny w przeglądarce i będzie komunikował się z backendem przez API.
