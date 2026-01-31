## Wymagania wstępne

Do uruchomienia aplikacji wymagane są:

- Python w wersji 3.10 lub nowszej
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

- `OPENAI_API_KEY` – Twój klucz API do OpenAI. Pozyskany z [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys)
- `GOOGLE_API_KEY` – Klucz API do usług Google (np. wyszukiwarka niestandardowa). Wygenerowany w Google Cloud Console.
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
