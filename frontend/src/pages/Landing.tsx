import { Link } from 'react-router-dom'
import { ArrowRight, Brain, BarChart2, Shield, Zap, TrendingUp, Award } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card'

const features = [
  {
    icon: Brain,
    title: 'ML-Powered Analysis',
    description: 'Advanced machine learning models trained on behavioral economics data to accurately predict your financial risk profile.',
  },
  {
    icon: BarChart2,
    title: 'SHAP Explanations',
    description: 'Transparent AI decisions backed by SHAP values — understand exactly which factors drive your risk assessment.',
  },
  {
    icon: Shield,
    title: 'Behavioral Insights',
    description: 'Identify cognitive biases and behavioral patterns that influence your financial decision-making.',
  },
  {
    icon: Zap,
    title: 'Instant Results',
    description: 'Get your comprehensive risk profile in seconds, with actionable recommendations tailored to your situation.',
  },
  {
    icon: TrendingUp,
    title: 'Investment Guidance',
    description: 'Personalized investment preference recommendations based on your risk tolerance and financial goals.',
  },
  {
    icon: Award,
    title: 'Financial Discipline Score',
    description: 'Track and improve your financial discipline with a comprehensive scoring system and progress tracking.',
  },
]

const stats = [
  { label: 'Accuracy Rate', value: '94%' },
  { label: 'Features Analyzed', value: '26+' },
  { label: 'Risk Categories', value: '3' },
  { label: 'Avg. Completion', value: '4 min' },
]

export function Landing() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative py-20 md:py-32 overflow-hidden">
        <div className="absolute inset-0 -z-10 bg-gradient-to-br from-primary/5 via-transparent to-primary/5" />
        <div className="container text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border bg-secondary text-secondary-foreground text-sm font-medium mb-8">
            <Brain className="h-4 w-4" />
            Behavioral Economics Powered
          </div>
          <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
            Understand Your{' '}
            <span className="text-primary">Financial Risk</span>{' '}
            Profile
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-10">
            Our AI analyzes your behavioral patterns and financial habits to give you a precise,
            explainable risk assessment — empowering smarter investment decisions.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/assessment">
              <Button size="lg" className="gap-2 text-base px-8">
                Start Free Assessment
                <ArrowRight className="h-5 w-5" />
              </Button>
            </Link>
            <Link to="/analytics">
              <Button size="lg" variant="outline" className="gap-2 text-base px-8">
                <BarChart2 className="h-5 w-5" />
                View Analytics
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="border-y bg-muted/30">
        <div className="container py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {stats.map((stat) => (
              <div key={stat.label}>
                <div className="text-3xl font-bold text-primary mb-1">{stat.value}</div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20">
        <div className="container">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">Why Choose RiskAI?</h2>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Combining behavioral economics with cutting-edge ML to deliver insights no traditional assessment can match.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature) => (
              <Card key={feature.title} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center mb-3">
                    <feature.icon className="h-5 w-5 text-primary" />
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                  <CardDescription>{feature.description}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 bg-muted/30">
        <div className="container">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4">How It Works</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {[
              { step: '01', title: 'Complete Assessment', desc: 'Answer 4 simple steps covering demographics, finances, and lifestyle.' },
              { step: '02', title: 'AI Analysis', desc: 'Our ML model analyzes 26+ behavioral and financial features in real-time.' },
              { step: '03', title: 'Get Insights', desc: 'Receive your risk profile, SHAP explanations, and personalized recommendations.' },
            ].map((item) => (
              <Card key={item.step} className="text-center">
                <CardContent className="pt-6">
                  <div className="text-4xl font-bold text-primary/30 mb-3">{item.step}</div>
                  <h3 className="font-semibold text-lg mb-2">{item.title}</h3>
                  <p className="text-muted-foreground text-sm">{item.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="container text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Know Your Risk Profile?</h2>
          <p className="text-muted-foreground mb-8 max-w-lg mx-auto">
            Join thousands of individuals who have gained clarity about their financial risk tolerance.
          </p>
          <Link to="/assessment">
            <Button size="lg" className="gap-2 text-base px-10">
              Begin Assessment Now
              <ArrowRight className="h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8 mt-auto">
        <div className="container flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <Brain className="h-4 w-4" />
            <span>RiskAI — Behavioral Risk Assessment</span>
          </div>
          <div>Built with behavioral economics & explainable AI</div>
        </div>
      </footer>
    </div>
  )
}
