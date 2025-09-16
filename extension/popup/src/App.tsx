import './App.css'
import { BackendStatus } from './components/BackendStatus'

function App() {
  return (
    <div className="popup-container">
      <div className="popup-header">
        <h2>Homepage Companion</h2>
        <p className="subtitle">Extension Features</p>
      </div>

      <div className="popup-content">
        <BackendStatus checkInterval={5000} />

        <div className="placeholder">
          <p>This popup is now built with React + Vite + TypeScript</p>
          <p>Ready for future development!</p>
        </div>
      </div>
    </div>
  )
}

export default App
