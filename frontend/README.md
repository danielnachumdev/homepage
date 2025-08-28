# Frontend

This is a React + Vite frontend application with a header component that displays backend connection status.

## Features

- **Header Component**: Displays application title and backend connection status
- **Real-time Status Monitoring**: Checks backend connectivity every 5 seconds
- **Visual Status Indicators**: Green dot for connected, red dot for disconnected
- **Error Handling**: Shows error details and last check time
- **Responsive Design**: Works on desktop and mobile devices

## Backend Health Check Setup

The frontend expects a health check endpoint at `/api/health` on your backend server. The endpoint should:

- Accept GET requests
- Return a 200 status code when healthy
- Be accessible at the URL specified in `VITE_BACKEND_URL` environment variable

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_BACKEND_URL=http://localhost:3000
```

### Backend Health Check Example

Here's a simple Express.js health check endpoint:

```javascript
app.get('/api/health', (req, res) => {
  res.status(200).json({ status: 'ok', timestamp: new Date().toISOString() });
});
```

## Development

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

## Project Structure

```
src/
├── components/
│   └── Header/
│       ├── Header.tsx          # Header component with status indicator
│       ├── Header.css          # Header styles
│       └── index.ts            # Component exports
├── hooks/
│   └── useBackendStatus.ts     # Hook for backend connectivity monitoring
├── config/
│   └── api.ts                  # API configuration and endpoints
├── App.tsx                     # Main application component
└── main.tsx                    # Application entry point
```

## Status Indicator

The header includes a real-time status indicator that:

- **Green Dot**: Backend is connected and responding
- **Red Dot**: Backend is disconnected or not responding
- **Warning Icon**: Shows when there are connection errors
- **Timestamp**: Displays when the last check was performed

The status is automatically checked every 5 seconds and updates in real-time.
