# Doctor AI Frontend

React-based frontend for the Doctor AI medical diagnosis assistant.

## Tech Stack

- React 18 with Vite
- React Router for navigation
- Axios for API calls

## Setup

```bash
# Install dependencies
npm install

# Configure API URL (optional)
cp .env.example .env
# Edit VITE_API_URL if needed (default: http://localhost:8000)

# Start development server
npm run dev
# Runs at http://localhost:3000

# Build for production
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   ├── pages/           # Page components
│   ├── services/        # API services
│   └── styles/          # CSS files
├── public/              # Static assets
└── vite.config.js       # Vite configuration
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
