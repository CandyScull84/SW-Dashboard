# SW Dashboard – Frontend

Frontend för SW Dashboard, ett webbaserat utvecklardashboard som visar information om utvecklingsaktivitet från GitLab.

Den här delen av projektet innehåller användargränssnittet, återanvändbara React-komponenter, API-kommunikation och egna React-hooks.

## Tekniker

- React
- JavaScript
- Vite
- Axios
- CSS
- PropTypes

## Funktioner

- Översikt över aktiva projekt.
- Visning av senaste push-händelser.
- Öppna merge requests.
- Övervakning av pipeline-statusar.
- Automatisk uppdatering av data.
- Automatisk scrollning med möjlighet till manuell styrning.
- Ljust och mörkt tema.
- Informationspanel med snabböversikt.
- Responsiv dashboardlayout.

## Projektstruktur

```text
src/
├── api/           # Kommunikation med backend
├── assets/        # Bilder och ikoner
├── components/    # Återanvändbara komponenter
├── hooks/         # Egna React-hooks
├── App.jsx        # Dashboardens huvudkomponent
├── App.css        # Styling för dashboarden
├── index.css      # Global styling
└── main.jsx       # Startpunkt för React
```

## Installation och uppstart

Installera beroenden:

```bash
npm install
```

Starta utvecklingsservern:

```bash
npm run dev
```

Frontend är normalt tillgänglig på:

http://localhost:5173

## Kommunikation med backend

Frontend kommunicerar med en backend utvecklad i Python och FastAPI.

Under lokal utveckling används Vites proxykonfiguration för att vidarebefordra API-anrop till:

```text
http://localhost:8088
```

API-adressen kan även konfigureras med miljövariabeln `VITE_API_URL`.

## Tillgängliga kommandon

| Kommando | Beskrivning |
|---|---|
| `npm run dev` | Startar utvecklingsservern |
| `npm run build` | Bygger frontend för produktion |
| `npm run lint` | Kontrollerar koden med ESLint |
| `npm run preview` | Förhandsgranskar produktionsbygget |

## Mer information

För information om backend, API-endpoints och hela applikationen, se [projektets huvud-README](../README.md).