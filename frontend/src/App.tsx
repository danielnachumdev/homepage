import { Header } from './components/Header'
import { Homepage } from './components/Homepage'
import { ChromeProfilesProvider } from './contexts/ChromeProfilesContext'
import { SettingsProvider } from './contexts/SettingsContext'
import './App.css'

function App() {

  return (
    <SettingsProvider>
      <ChromeProfilesProvider>
        <Header />
        <Homepage />
      </ChromeProfilesProvider>
    </SettingsProvider>
  )
}

export default App
