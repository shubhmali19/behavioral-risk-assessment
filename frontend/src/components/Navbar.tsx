import { Link, useLocation } from 'react-router-dom'
import { Moon, Sun, BarChart2, Brain } from 'lucide-react'
import { Button } from './ui/button'
import { useTheme } from '../contexts/ThemeContext'
import { cn } from '../lib/utils'

const navLinks = [
  { href: '/', label: 'Home' },
  { href: '/assessment', label: 'Assessment' },
  { href: '/history', label: 'History' },
  { href: '/analytics', label: 'Analytics' },
]

export function Navbar() {
  const { resolvedTheme, setTheme } = useTheme()
  const location = useLocation()

  const toggleTheme = () => {
    setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')
  }

  return (
    <nav className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2 font-bold text-lg">
          <Brain className="h-6 w-6 text-primary" />
          <span className="hidden sm:inline">RiskAI</span>
        </Link>

        <div className="flex items-center gap-1">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              to={link.href}
              className={cn(
                "px-3 py-2 text-sm rounded-md transition-colors hover:bg-accent hover:text-accent-foreground",
                location.pathname === link.href
                  ? "bg-accent text-accent-foreground font-medium"
                  : "text-muted-foreground"
              )}
            >
              {link.label}
            </Link>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Toggle theme">
            {resolvedTheme === 'dark' ? (
              <Sun className="h-5 w-5" />
            ) : (
              <Moon className="h-5 w-5" />
            )}
          </Button>
          <Link to="/analytics">
            <Button variant="ghost" size="icon" aria-label="Analytics">
              <BarChart2 className="h-5 w-5" />
            </Button>
          </Link>
        </div>
      </div>
    </nav>
  )
}
