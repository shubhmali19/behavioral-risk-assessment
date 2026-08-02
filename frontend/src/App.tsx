import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ThemeProvider } from './contexts/ThemeContext'
import { Navbar } from './components/Navbar'
import { Landing } from './pages/Landing'
import { Assessment } from './pages/Assessment'
import { Results } from './pages/Results'
import { History } from './pages/History'
import { Analytics } from './pages/Analytics'

function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-background">
          <Navbar />
          <main>
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route path="/assessment" element={<Assessment />} />
              <Route path="/results/:id" element={<Results />} />
              <Route path="/history" element={<History />} />
              <Route path="/analytics" element={<Analytics />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </ThemeProvider>
  )
}

export default App
