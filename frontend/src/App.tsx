import { useComponentLogger } from './hooks/useLogger'
import { useRef } from 'react'
import { Header } from './components/Header'
import './App.css'

function App() {
  const logger = useComponentLogger('App');
  const renderCountRef = useRef(0);

  // Increment render count on each render
  renderCountRef.current += 1;

  // Test logging - should appear in console AND be sent to backend
  logger.debug('App component mounted', { renderCount: renderCountRef.current });
  logger.info('Application started', { renderCount: renderCountRef.current });
  logger.warning('This is a test warning', { renderCount: renderCountRef.current });
  logger.error('This is a test error', { renderCount: renderCountRef.current });

  return (
    <>
      <Header />
      <div>
        <h1>Minimal App - A/B Testing</h1>
        <p>Added Header component</p>
        <p>Render count: {renderCountRef.current}</p>
      </div>
    </>
  )
}

export default App
