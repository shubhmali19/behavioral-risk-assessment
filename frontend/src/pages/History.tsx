import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Clock, ChevronRight, Trash2, AlertCircle } from 'lucide-react'
import { Card, CardContent } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { getAssessments } from '../api/assessments'
import type { AssessmentRecord } from '../types'

function getRiskBadgeVariant(category: string): 'success' | 'warning' | 'danger' {
  switch (category) {
    case 'Low': return 'success'
    case 'Medium': return 'warning'
    case 'High': return 'danger'
    default: return 'success'
  }
}

export function History() {
  const [items, setItems] = useState<AssessmentRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // Try to get from API first, fallback to localStorage
    getAssessments()
      .then((data) => {
        setItems(data.items)
      })
      .catch(() => {
        // Fallback to localStorage
        const stored = localStorage.getItem('assessment_history')
        if (stored) {
          try {
            setItems(JSON.parse(stored))
          } catch {
            setError('Failed to load history')
          }
        }
      })
      .finally(() => setLoading(false))
  }, [])

  const clearHistory = () => {
    if (confirm('Clear all local assessment history?')) {
      localStorage.removeItem('assessment_history')
      setItems([])
    }
  }

  if (loading) {
    return (
      <div className="container py-20 text-center text-muted-foreground">
        Loading history...
      </div>
    )
  }

  return (
    <div className="container py-10 max-w-3xl">
      <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
        <div>
          <h1 className="text-3xl font-bold">Assessment History</h1>
          <p className="text-muted-foreground mt-1">{items.length} assessment{items.length !== 1 ? 's' : ''} found</p>
        </div>
        <div className="flex gap-2">
          {items.length > 0 && (
            <Button variant="outline" size="sm" onClick={clearHistory} className="gap-1">
              <Trash2 className="h-4 w-4" /> Clear Local
            </Button>
          )}
          <Link to="/assessment">
            <Button size="sm">New Assessment</Button>
          </Link>
        </div>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-destructive mb-6 p-3 rounded-md bg-destructive/10">
          <AlertCircle className="h-4 w-4" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {items.length === 0 ? (
        <Card>
          <CardContent className="py-16 text-center">
            <Clock className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="font-semibold text-lg mb-2">No assessments yet</h3>
            <p className="text-muted-foreground mb-6">Complete your first assessment to see results here.</p>
            <Link to="/assessment">
              <Button>Start Assessment</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <Link key={item.id} to={`/results/${item.id}`}>
              <Card className="hover:shadow-md transition-shadow cursor-pointer group">
                <CardContent className="flex items-center justify-between py-4 px-6">
                  <div className="flex items-center gap-4">
                    <div className="text-2xl font-bold text-primary">
                      {item.prediction?.financial_decision_score != null
                        ? item.prediction.financial_decision_score.toFixed(1)
                        : '—'}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <Badge variant={getRiskBadgeVariant(item.prediction?.risk_category ?? '')}>
                          {item.prediction?.risk_category ?? 'Unknown'} Risk
                        </Badge>
                        {item.prediction?.risk_confidence != null && (
                          <span className="text-xs text-muted-foreground">
                            {(item.prediction.risk_confidence * 100).toFixed(0)}% confidence
                          </span>
                        )}
                      </div>
                      <div className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {new Date(item.created_at).toLocaleDateString('en-IN', {
                          day: 'numeric', month: 'short', year: 'numeric',
                          hour: '2-digit', minute: '2-digit'
                        })}
                      </div>
                    </div>
                  </div>
                  <ChevronRight className="h-5 w-5 text-muted-foreground group-hover:text-foreground transition-colors" />
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
