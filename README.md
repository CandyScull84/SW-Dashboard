# SW Dashboard

Ett webbaserat utvecklardashboard som samlar och visualiserar information från GitLab via GitLab REST API.

SW Dashboard ger en överblick över aktiva projekt, senaste push-händelser, öppna merge requests och pipeline-statusar. Syftet är att göra det enklare att följa utvecklingsarbetet och snabbt få en bild av vad som händer i olika projekt.

Applikationen är utvecklad som ett fullstackprojekt med **Python och FastAPI i backend** samt **React och Vite i frontend**.

## Funktioner

### Merge Requests
- Hämtar öppna merge requests från projekt i en GitLab-grupp.
- Filtrerar bort utkast (Draft/WIP).
- Visar bland annat projekt, författare, granskare och datum.
- Ger möjlighet att öppna merge requests direkt i GitLab.

### Push-händelser
- Hämtar de senaste push-händelserna från GitLab.
- Visar aktuell utvecklingsaktivitet i olika projekt.
- Sorterar händelser efter tidpunkt.

### Aktiva projekt
- Identifierar projekt som nyligen haft aktivitet.
- Visar projektinformation och aktivitetssammanställningar.
- Ger en överblick över pågående utvecklingsarbete.

### Pipeline-övervakning
- Hämtar information om pipelines från GitLab.
- Identifierar relevanta statusar, exempelvis failed, running, pending och canceled.
- Visar pipeline-information i dashboarden.

### Dashboard och användargränssnitt
- Automatisk uppdatering av data.
- Automatisk scrollning som kan aktiveras och inaktiveras.
- Ljust och mörkt tema.
- Komponentbaserat gränssnitt i React.
- Informationspanel med snabböversikt.
- Responsiv layout.

### Teamstatus – experimentell funktion

En funktion för att undersöka teammedlemmars aktivitet via GitLab har också utvecklats.

Funktionen finns kvar i projektet men visas för närvarande inte i dashboardens huvudsakliga gränssnitt. En framtida vidareutveckling skulle kunna innebära integration med andra tjänster, exempelvis Microsoft Teams.

## Tekniker

### Backend
- Python
- FastAPI
- GitLab REST API
- HTTPX
- Requests
- Uvicorn

### Frontend
- React
- JavaScript
- Vite
- Axios
- CSS
- PropTypes

## Projektstruktur

```text
SW-Dashboard/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── api/
│   │   ├── assets/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── App.jsx
│   │   └── main.jsx
│   └── package.json
├── src/
│   └── sw_dashboard/
│       ├── api/
│       │   ├── current_projects.py
│       │   ├── gitlab_client.py
│       │   ├── merge_requests.py
│       │   ├── mock_data.py
│       │   ├── pipelines.py
│       │   └── team_status.py
│       ├── config.py
│       ├── main.py
│       └── server.py
├── pyproject.toml
└── README.md
```

## Installation och uppstart

### Förutsättningar

- Python 3.13 eller senare
- Node.js och npm
- Tillgång till GitLab och en API-token för att använda riktig GitLab-data

### 1. Klona projektet

```bash
git clone https://github.com/CandyScull84/SW-Dashboard.git
cd SW-Dashboard
```

*Observera att länken börjar fungera när projektet har publicerats på GitHub.*

### 2. Konfigurera backend

Skapa en virtuell Python-miljö:

```bash
python -m venv .venv
```

Aktivera miljön i Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

För macOS/Linux:

```bash
source .venv/bin/activate
```

Installera projektets Python-beroenden:

```bash
pip install -e .
```

### 3. Miljövariabler

Backend använder miljövariabler för GitLab-konfigurationen.

Exempel:

```env
USE_MOCK=true
GITLAB_API_URL=https://gitlab.com/api/v4
ACCESS_TOKEN=din_gitlab_token
GITLAB_GROUP_ID=ditt_grupp_id
GITLAB_MEMBER_GROUP_ID=ditt_medlemsgrupp_id
```

Använd egna GitLab-uppgifter och grupp-ID:n.

**API-token och andra känsliga uppgifter ska aldrig publiceras på GitHub.**

### 4. Starta backend

Kör från projektets rotmapp:

```bash
python -m uvicorn sw_dashboard.server:app --reload --port 8088
```

Backend använder följande API-endpoints:

| Endpoint | Beskrivning |
|---|---|
| `/merge-requests` | Öppna merge requests |
| `/push-events` | Senaste push-händelserna |
| `/failing-pipelines` | Pipeline-övervakning |
| `/active-projects` | Aktiva projekt |
| `/team-status` | Experimentell teamstatus |

### 5. Starta frontend

Öppna en separat terminal och kör:

```bash
cd frontend
npm install
npm run dev
```

Frontend startas normalt på:

http://localhost:5173

Under utveckling använder Vite en proxy för att vidarebefordra API-anrop till FastAPI-backend på port `8088`.

## Demoläge

SW Dashboard innehåller ett inbyggt demoläge med fiktiva projekt, användare och utvecklingsaktiviteter.

Demoläget är aktiverat som standard och gör det möjligt att köra och utforska dashboarden utan tillgång till en GitLab-server eller API-token.

För att använda riktig GitLab-data kan demoläget inaktiveras genom att ange följande i en `.env`-fil:

```env
USE_MOCK=false
```

Då behöver även GitLab-konfigurationen och en giltig API-token anges.

## Utveckling och testning

### Frontend

Kontrollera koden med ESLint:

```bash
cd frontend
npm run lint
```

Bygg frontend för produktion:

```bash
npm run build
```

### Backend

Projektet innehåller även Python-skript för manuell testning av API-funktionaliteten.

Installations- och testkommandon behöver verifieras efter anpassningen av projektet för offentlig publicering.

## Möjlig vidareutveckling

- Förbättra felhantering och laddningsindikatorer.
- Utöka möjligheterna att filtrera projekt.
- Undersöka integrationer för teamaktivitet.
- Vidareutveckla dokumentation för driftsättning.

## Om projektet

SW Dashboard utvecklades som ett praktiskt fullstackprojekt med fokus på att integrera externa API:er och presentera utvecklingsaktivitet i ett tydligt och lättöverskådligt gränssnitt.

Projektet visar erfarenhet av:

- Backendutveckling med Python och FastAPI.
- Integration med REST API:er.
- Asynkron datahämtning.
- Databearbetning, filtrering och sammanställning.
- Frontendutveckling med React.
- Återanvändbara komponenter och egna React-hooks.
- Tillståndshantering och automatisk datauppdatering.
- Gränssnittsdesign och visualisering av information.

Den offentliga portfolioversionen är avsedd att visa applikationens uppbyggnad, funktioner och implementation utan att exponera konfidentiell information.