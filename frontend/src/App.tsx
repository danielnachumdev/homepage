import { Header } from './components/Header'
import { Homepage } from './components/Homepage'
import { useComponentLogger } from './hooks/useLogger'
import './App.css'

function App() {
  const logger = useComponentLogger('App');

  // Test logging - should appear in console AND be sent to backend
  logger.debug('App component mounted');
  logger.info('Application started');
  logger.warning('This is a test warning');
  logger.error('This is a test error');

  return (
    <>
      <Header />
      <Homepage />
    </>
  )
}

export default App
