import { useComponentLogger } from './hooks/useLogger'
import { useRef, useEffect } from 'react'
import { Header } from './components/Header'
import { Homepage } from './components/Homepage/Homepage'
import { usePerformanceTracking } from './hooks/usePerformanceTracking'
import { SettingsProvider } from './contexts/SettingsContext'
import './App.css'

function App() {
  const logger = useComponentLogger('App');
  const { trackApiCall, renderCount } = usePerformanceTracking('App');
  const renderCountRef = useRef(0);

  // Increment render count on each render
  renderCountRef.current += 1;

  // Only log on mount, not on every render
  useEffect(() => {
    logger.debug('App component mounted', { renderCount: renderCountRef.current });
    logger.info('Application started', { renderCount: renderCountRef.current });
    logger.warning('This is a test warning', { renderCount: renderCountRef.current });
    logger.error('This is a test error', { renderCount: renderCountRef.current });
  }, []); // Empty dependency array - only run on mount

  return (
    <SettingsProvider>
      <Header />
      <Homepage />
      <div>
        <h1>Minimal App - A/B Testing</h1>
        <p>Added Header component</p>
        <p>Render count: {renderCountRef.current}</p>
      </div>
    </SettingsProvider>
  )
}

export default App
