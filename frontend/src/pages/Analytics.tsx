import { useEffect, useState } from 'react'
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  BarChart, Bar,
} from 'recharts'
import { Loader2, AlertCircle, BarChart2 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card'
import { getAnalytics } from '../api/assessments'
import type { AnalyticsResponse } from '../types'

const RISK_COLORS: Record<string, string> = {
  Low: '#22c55e',
  Medium: '#f59e0b',
  High: '#ef4444',
}

const PIE_COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#06b6d4']

export function Analytics() {
  const [data, setData] = useState<AnalyticsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getAnalytics()
      .then(setData)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="container py-20 flex items-center justify-center gap-3">
        <Loader2 className="h-6 w-6 animate-spin text-primary" />
        <span className="text-muted-foreground">Loading analytics...</span>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="container py-20 text-center">
        <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
        <h2 className="text-xl font-semibold mb-2">Failed to load analytics</h2>
        <p className="text-muted-foreground">{error || 'No data available'}</p>
      </div>
    )
  }

  const riskDist = Object.entries(data.risk_distribution || {}).map(([name, value]) => ({
    name, value,
  }))

  const investDist = Object.entries(data.investment_distribution || {}).map(([name, value]) => ({
    name, value,
  }))

  const avgScores = [
    { metric: 'Financial Decision', score: data.avg_financial_decision_score },
    { metric: 'Behavioral Composite', score: data.avg_behavioral_composite_score },
    { metric: 'Financial Discipline', score: data.avg_financial_discipline_score },
  ]

  return (
    <div className="container py-10 max-w-5xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <BarChart2 className="h-8 w-8 text-primary" />
          Analytics Dashboard
        </h1>
        <p className="text-muted-foreground mt-1">Aggregated insights across all assessments</p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Assessments" value={data.total_assessments} />
        {avgScores.map((s) => (
          <StatCard key={s.metric} label={s.metric} value={s.score?.toFixed(1) ?? '—'} />
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-6">
        {/* Risk Distribution */}
        {riskDist.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Risk Distribution</CardTitle>
              <CardDescription>Breakdown of risk categories across assessments</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={riskDist}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, percent }: { name?: string; percent?: number }) => `${name ?? ''} ${((percent ?? 0) * 100).toFixed(0)}%`}
                    >
                      {riskDist.map((entry) => (
                        <Cell key={entry.name} fill={RISK_COLORS[entry.name] || '#6b7280'} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Investment Preference Distribution */}
        {investDist.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Investment Preferences</CardTitle>
              <CardDescription>Distribution of recommended investment types</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={investDist}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="value"
                      label={({ percent }: { percent?: number }) => `${((percent ?? 0) * 100).toFixed(0)}%`}
                    >
                      {investDist.map((entry, i) => (
                        <Cell key={entry.name} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(v, n) => [v, n]} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Average Scores Bar Chart */}
      {avgScores.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Average Score Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={avgScores}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis dataKey="metric" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="score" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Assessments over time */}
      {data.assessments_by_date && data.assessments_by_date.length > 0 && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Assessments Over Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data.assessments_by_date}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                  <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="count" stroke="#3b82f6" name="Assessments" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <Card>
      <CardContent className="pt-4 pb-4">
        <div className="text-2xl font-bold text-primary">{value}</div>
        <div className="text-xs text-muted-foreground mt-1">{label}</div>
      </CardContent>
    </Card>
  )
}
