import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import {
  RadialBarChart, RadialBar, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Cell,
} from 'recharts'
import { AlertCircle, Loader2, CheckCircle, TrendingUp, Brain, Shield, ArrowLeft, Save, Clock } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { Separator } from '../components/ui/separator'
import { getAssessment } from '../api/assessments'
import type { PredictionResult, AssessmentResponse } from '../types'

function getRiskColor(category: string) {
  switch (category) {
    case 'Low': return '#22c55e'
    case 'Medium': return '#f59e0b'
    case 'High': return '#ef4444'
    default: return '#6b7280'
  }
}

function getRiskBadgeVariant(category: string): 'success' | 'warning' | 'danger' {
  switch (category) {
    case 'Low': return 'success'
    case 'Medium': return 'warning'
    case 'High': return 'danger'
    default: return 'success'
  }
}

function ScoreCircle({ score, label, color }: { score: number; label: string; color: string }) {
  return (
    <div className="flex flex-col items-center gap-1">
      <div
        className="text-4xl font-bold"
        style={{ color }}
      >
        {typeof score === 'number' ? score.toFixed(1) : score}
      </div>
      <div className="text-xs text-muted-foreground text-center">{label}</div>
    </div>
  )
}

export function Results() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [assessment, setAssessment] = useState<{ prediction: PredictionResult; id: string; created_at?: string } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return

    // First try sessionStorage (just-submitted assessment)
    const stored = sessionStorage.getItem(`assessment_${id}`)
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        setAssessment(parsed)
        setLoading(false)
        return
      } catch {
        // fall through to API
      }
    }

    // Fetch from API
    getAssessment(id)
      .then((data: AssessmentResponse) => {
        setAssessment({ prediction: data.data, id: data.assessment_id, created_at: undefined })
      })
      .catch((err: Error) => {
        setError(err.message)
      })
      .finally(() => setLoading(false))
  }, [id])

  const saveToHistory = () => {
    if (!assessment) return
    const history = JSON.parse(localStorage.getItem('assessment_history') || '[]')
    const exists = history.find((h: { id: string }) => h.id === assessment.id)
    if (!exists) {
      history.unshift({
        id: assessment.id,
        created_at: assessment.created_at || new Date().toISOString(),
        risk_category: assessment.prediction.risk_category,
        financial_decision_score: assessment.prediction.financial_decision_score,
        confidence: assessment.prediction.risk_confidence,
      })
      localStorage.setItem('assessment_history', JSON.stringify(history.slice(0, 50)))
      alert('Assessment saved to history!')
    } else {
      alert('Already saved in history.')
    }
  }

  if (loading) {
    return (
      <div className="container py-20 flex items-center justify-center gap-3">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
        <span className="text-muted-foreground">Loading your results...</span>
      </div>
    )
  }

  if (error || !assessment) {
    return (
      <div className="container py-20 text-center">
        <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
        <h2 className="text-xl font-semibold mb-2">Could not load results</h2>
        <p className="text-muted-foreground mb-6">{error || 'Assessment not found'}</p>
        <Button onClick={() => navigate('/assessment')}>Try Again</Button>
      </div>
    )
  }

  const { prediction } = assessment
  const riskColor = getRiskColor(prediction.risk_category)

  // Gauge data
  const gaugeData = [
    { name: 'Risk', value: prediction.risk_confidence * 100, fill: riskColor },
  ]

  // SHAP bar chart data (top 10 by absolute value)
  const shapEntries = Object.entries(prediction.shap_values || {})
    .map(([k, v]) => ({ feature: k.replace(/_/g, ' '), value: v, absValue: Math.abs(v) }))
    .sort((a, b) => b.absValue - a.absValue)
    .slice(0, 10)

  return (
    <div className="container py-8 max-w-4xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-8 flex-wrap gap-4">
        <div>
          <Link to="/assessment" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground mb-2">
            <ArrowLeft className="h-4 w-4" /> Back to Assessment
          </Link>
          <h1 className="text-3xl font-bold">Your Risk Assessment Results</h1>
          {assessment.created_at && (
            <p className="text-sm text-muted-foreground flex items-center gap-1 mt-1">
              <Clock className="h-3 w-3" />
              {new Date(assessment.created_at).toLocaleDateString()}
            </p>
          )}
        </div>
        <Button variant="outline" onClick={saveToHistory} className="gap-2">
          <Save className="h-4 w-4" /> Save to History
        </Button>
      </div>

      {/* Main Risk Card */}
      <div className="grid md:grid-cols-2 gap-6 mb-6">
        {/* Risk Gauge */}
        <Card>
          <CardHeader>
            <CardTitle>Risk Profile</CardTitle>
            <CardDescription>Your overall financial risk category</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col items-center">
            <div className="relative w-48 h-48">
              <ResponsiveContainer width="100%" height="100%">
                <RadialBarChart
                  cx="50%"
                  cy="50%"
                  innerRadius="60%"
                  outerRadius="90%"
                  startAngle={90}
                  endAngle={-270}
                  data={gaugeData}
                >
                  <RadialBar dataKey="value" cornerRadius={8} background={{ fill: 'hsl(var(--muted))' }} />
                </RadialBarChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-bold" style={{ color: riskColor }}>
                  {(prediction.risk_confidence * 100).toFixed(0)}%
                </span>
                <span className="text-xs text-muted-foreground">Confidence</span>
              </div>
            </div>
            <Badge variant={getRiskBadgeVariant(prediction.risk_category)} className="text-base px-4 py-1 mt-2">
              {prediction.risk_category} Risk
            </Badge>
          </CardContent>
        </Card>

        {/* Investment Preference */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-primary" />
              Investment Recommendation
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="text-sm text-muted-foreground mb-1">Preferred Investment Type</div>
              <div className="text-xl font-semibold text-primary">{prediction.investment_preference}</div>
            </div>
            <Separator />
            {/* Score trio */}
            <div className="grid grid-cols-3 gap-4 pt-2">
              <ScoreCircle
                score={prediction.financial_decision_score}
                label="Financial Decision"
                color="#3b82f6"
              />
              <ScoreCircle
                score={prediction.behavioral_composite_score}
                label="Behavioral Composite"
                color="#8b5cf6"
              />
              <ScoreCircle
                score={prediction.financial_discipline_score}
                label="Discipline Score"
                color="#10b981"
              />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* SHAP Feature Importance */}
      {shapEntries.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-primary" />
              Feature Importance (SHAP Values)
            </CardTitle>
            <CardDescription>Top 10 factors driving your risk assessment</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={shapEntries} layout="vertical" margin={{ left: 20, right: 20 }}>
                  <XAxis type="number" tick={{ fontSize: 11 }} />
                  <YAxis type="category" dataKey="feature" width={140} tick={{ fontSize: 11 }} />
                  <Tooltip
                    formatter={(v: unknown) => [typeof v === 'number' ? v.toFixed(4) : String(v), 'SHAP Value']}
                    contentStyle={{ fontSize: 12 }}
                  />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {shapEntries.map((entry, i) => (
                      <Cell key={i} fill={entry.value >= 0 ? '#3b82f6' : '#ef4444'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Blue = increases risk score, Red = decreases risk score
            </p>
          </CardContent>
        </Card>
      )}

      {/* Behavioral Biases */}
      {prediction.behavioral_biases && prediction.behavioral_biases.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary" />
              Detected Behavioral Biases
            </CardTitle>
            <CardDescription>Cognitive patterns that may affect your financial decisions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {prediction.behavioral_biases.map((bias, i) => (
                <Badge key={i} variant="outline" className="text-sm py-1 px-3">
                  {bias}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recommendations */}
      {prediction.recommendations && prediction.recommendations.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              Personalized Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {prediction.recommendations.map((rec, i) => (
                <li key={i} className="flex items-start gap-3">
                  <span className="flex-shrink-0 h-6 w-6 rounded-full bg-primary/10 text-primary text-xs flex items-center justify-center font-medium">
                    {i + 1}
                  </span>
                  <span className="text-sm">{rec}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="flex flex-wrap gap-4">
        <Link to="/assessment">
          <Button variant="outline">Take New Assessment</Button>
        </Link>
        <Link to="/history">
          <Button variant="outline">View History</Button>
        </Link>
        <Link to="/analytics">
          <Button>View Analytics Dashboard</Button>
        </Link>
      </div>
    </div>
  )
}
