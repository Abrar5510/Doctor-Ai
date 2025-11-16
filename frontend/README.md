# Doctor AI Frontend

A modern React-based frontend for the Doctor AI medical diagnosis assistant.

## Features

- Modern React 18 with Vite for fast development
- Clean and responsive UI design
- Real-time diagnosis results
- Patient information management
- Confidence level visualization
- Differential diagnosis display
- Medical recommendations

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **CSS3** - Styling

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install
```

### Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Update `.env` with your API URL (default: `http://localhost:8000`)

### Development

Start the development server:

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

### Building for Production

```bash
npm run build
```

The built files will be in the `dist` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── Header.jsx
│   │   ├── DiagnosisForm.jsx
│   │   └── ResultsDisplay.jsx
│   ├── pages/           # Page components
│   ├── services/        # API services
│   │   └── api.js
│   ├── styles/          # CSS files
│   │   ├── index.css
│   │   ├── App.css
│   │   ├── Header.css
│   │   ├── DiagnosisForm.css
│   │   └── ResultsDisplay.css
│   ├── utils/           # Utility functions
│   ├── App.jsx          # Main App component
│   └── main.jsx         # Entry point
├── public/              # Static assets
├── index.html           # HTML template
├── vite.config.js       # Vite configuration
└── package.json         # Dependencies

```

## API Integration

The frontend connects to the backend API using Axios. The API client is configured in `src/services/api.js`.

### Main Endpoints

- `POST /api/v1/diagnose` - Submit symptoms for diagnosis

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Contributing

1. Make changes in a feature branch
2. Test thoroughly
3. Submit a pull request

## License

Copyright © 2024 Doctor AI
