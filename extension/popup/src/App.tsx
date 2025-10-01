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

      </div>
    </div>
  )
}

export default App
