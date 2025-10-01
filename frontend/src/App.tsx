import { useComponentLogger } from './hooks/useLogger'
import { useEffect } from 'react'
import { Header } from './components/Header'
import { Homepage } from './components/Homepage/Homepage'
import { usePerformanceTracking } from './hooks/usePerformanceTracking'
import { SettingsProvider } from './contexts/SettingsContext'
import './App.css'

function App() {
  const logger = useComponentLogger('App');
  const { trackApiCall } = usePerformanceTracking('App');

  // Only log on mount, not on every render
  useEffect(() => {
    logger.debug('App component mounted');
    logger.info('Application started');
  }, []); // Empty dependency array - only run on mount

  return (
    <SettingsProvider>
      <Header />
      <Homepage />
    </SettingsProvider>
  )
}

export default App
