import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { ChevronRight, ChevronLeft, CheckCircle, Loader2 } from 'lucide-react'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select'
import { Progress } from '../components/ui/progress'
import { postAssessment } from '../api/assessments'
import type { AssessmentInput } from '../types'

// Exact literals must match backend Pydantic enums — see docs/api-contract.json
const schema = z.object({
  // Demographics
  age: z.coerce.number().min(18, 'Must be at least 18').max(100),
  gender: z.enum(['Male', 'Female', 'Other']),
  education: z.enum(['High School', 'Graduate', 'Post Graduate', 'PhD']),
  occupation: z.enum(['Salaried', 'Self-Employed', 'Business', 'Freelancer', 'Student', 'Retired']),
  income_level: z.enum(['Low', 'Middle', 'High']),
  marital_status: z.enum(['Single', 'Married', 'Divorced', 'Widowed']),
  dependents: z.coerce.number().min(0).max(10),
  location: z.enum(['Urban', 'Semi-Urban', 'Rural']),
  employment_type: z.enum(['Full-Time', 'Part-Time', 'Contract', 'Unemployed']),
  years_of_experience: z.coerce.number().min(0).max(50),
  // Financial
  monthly_income: z.coerce.number().gt(0, 'Must be greater than 0'),
  monthly_expenses: z.coerce.number().gt(0, 'Must be greater than 0'),
  savings_rate: z.coerce.number().min(0).max(100),
  emergency_fund_months: z.coerce.number().min(0).max(36),
  total_debt: z.coerce.number().min(0),
  loan_amount: z.coerce.number().min(0),
  credit_score: z.coerce.number().min(300, 'Min 300').max(900, 'Max 900'),
  investment_experience_years: z.coerce.number().min(0).max(50),
  investment_frequency: z.enum(['Never', 'Rarely', 'Monthly', 'Weekly']),
  insurance_coverage: z.enum(['None', 'Basic', 'Comprehensive']),
  // Lifestyle
  shopping_frequency: z.enum(['Rarely', 'Monthly', 'Weekly', 'Daily']),
  online_spending_pct: z.coerce.number().min(0).max(100),
  luxury_spending_pct: z.coerce.number().min(0).max(100),
  subscription_count: z.coerce.number().min(0).max(30),
  gaming_expenses_monthly: z.coerce.number().min(0),
  travel_expenses_annual: z.coerce.number().min(0),
})

type FormData = z.input<typeof schema>
type FormOutput = z.output<typeof schema>

const STEPS = ['Demographics', 'Financial Profile', 'Lifestyle', 'Review & Submit']

function FieldRow({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1.5">
      <Label>{label}</Label>
      {children}
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  )
}

interface SelectFieldProps {
  label: string
  value: string
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  onChange: (v: any) => void
  options: { value: string; label: string }[]
  error?: string
  placeholder?: string
}

function SelectField({ label, value, onChange, options, error, placeholder }: SelectFieldProps) {
  return (
    <FieldRow label={label} error={error}>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger>
          <SelectValue placeholder={placeholder || `Select ${label.toLowerCase()}`} />
        </SelectTrigger>
        <SelectContent>
          {options.map((o) => (
            <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
          ))}
        </SelectContent>
      </Select>
    </FieldRow>
  )
}

export function Assessment() {
  const [step, setStep] = useState(0)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const { register, handleSubmit, trigger, setValue, watch, formState: { errors } } = useForm<FormData, unknown, FormOutput>({
    resolver: zodResolver(schema),
    defaultValues: {
      age: 30,
      dependents: 0,
      years_of_experience: 5,
      monthly_income: 50000,
      monthly_expenses: 30000,
      savings_rate: 20,
      emergency_fund_months: 3,
      total_debt: 0,
      loan_amount: 0,
      credit_score: 700,
      investment_experience_years: 2,
      online_spending_pct: 30,
      luxury_spending_pct: 10,
      subscription_count: 3,
      gaming_expenses_monthly: 0,
      travel_expenses_annual: 20000,
    },
  })

  const stepFields: Record<number, (keyof FormData)[]> = {
    0: ['age', 'gender', 'education', 'occupation', 'income_level', 'marital_status', 'dependents', 'location', 'employment_type', 'years_of_experience'],
    1: ['monthly_income', 'monthly_expenses', 'savings_rate', 'emergency_fund_months', 'total_debt', 'loan_amount', 'credit_score', 'investment_experience_years', 'investment_frequency', 'insurance_coverage'],
    2: ['shopping_frequency', 'online_spending_pct', 'luxury_spending_pct', 'subscription_count', 'gaming_expenses_monthly', 'travel_expenses_annual'],
  }

  const nextStep = async () => {
    const fields = stepFields[step]
    if (fields) {
      const valid = await trigger(fields)
      if (!valid) return
    }
    setStep((s) => Math.min(s + 1, STEPS.length - 1))
  }

  const prevStep = () => setStep((s) => Math.max(s - 1, 0))

  const onSubmit = async (data: FormOutput) => {
    setIsSubmitting(true)
    setError(null)
    try {
      const response = await postAssessment(data as AssessmentInput)
      const { assessment_id: id, data: prediction } = response
      // Cache for an immediate render; /results/:id refetches by id if absent.
      sessionStorage.setItem(`assessment_${id}`, JSON.stringify({ id, prediction }))
      navigate(`/results/${id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit assessment')
    } finally {
      setIsSubmitting(false)
    }
  }

  const values = watch()

  return (
    <div className="container py-10 max-w-2xl">
      {/* Progress */}
      <div className="mb-8">
        <div className="flex justify-between mb-2">
          {STEPS.map((s, i) => (
            <span
              key={s}
              className={`text-xs font-medium ${i <= step ? 'text-primary' : 'text-muted-foreground'}`}
            >
              {s}
            </span>
          ))}
        </div>
        <Progress value={((step) / (STEPS.length - 1)) * 100} className="h-2" />
        <p className="text-sm text-muted-foreground mt-2">Step {step + 1} of {STEPS.length}</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit as Parameters<typeof handleSubmit>[0])}>
        {/* Step 0: Demographics */}
        {step === 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Demographics</CardTitle>
              <CardDescription>Tell us about yourself</CardDescription>
            </CardHeader>
            <CardContent className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <FieldRow label="Age" error={errors.age?.message}>
                <Input type="number" {...register('age')} />
              </FieldRow>
              <SelectField
                label="Gender"
                value={values.gender || ''}
                onChange={(v) => setValue('gender', v)}
                error={errors.gender?.message}
                options={[
                  { value: 'Male', label: 'Male' },
                  { value: 'Female', label: 'Female' },
                  { value: 'Other', label: 'Other' },
                ]}
              />
              <SelectField
                label="Education"
                value={values.education || ''}
                onChange={(v) => setValue('education', v)}
                error={errors.education?.message}
                options={[
                  { value: 'High School', label: 'High School' },
                  { value: 'Graduate', label: 'Graduate (Bachelor\'s)' },
                  { value: 'Post Graduate', label: 'Post Graduate (Master\'s)' },
                  { value: 'PhD', label: 'PhD / Doctorate' },
                ]}
              />
              <SelectField
                label="Occupation"
                value={values.occupation || ''}
                onChange={(v) => setValue('occupation', v)}
                error={errors.occupation?.message}
                options={[
                  { value: 'Salaried', label: 'Salaried (Employee)' },
                  { value: 'Self-Employed', label: 'Self-Employed' },
                  { value: 'Business', label: 'Business Owner' },
                  { value: 'Freelancer', label: 'Freelancer / Consultant' },
                  { value: 'Student', label: 'Student' },
                  { value: 'Retired', label: 'Retired' },
                ]}
              />
              <SelectField
                label="Income Level"
                value={values.income_level || ''}
                onChange={(v) => setValue('income_level', v)}
                error={errors.income_level?.message}
                options={[
                  { value: 'Low', label: 'Low (< ₹5L/yr)' },
                  { value: 'Middle', label: 'Middle (₹5–15L/yr)' },
                  { value: 'High', label: 'High (> ₹15L/yr)' },
                ]}
              />
              <SelectField
                label="Marital Status"
                value={values.marital_status || ''}
                onChange={(v) => setValue('marital_status', v)}
                error={errors.marital_status?.message}
                options={[
                  { value: 'Single', label: 'Single' },
                  { value: 'Married', label: 'Married' },
                  { value: 'Divorced', label: 'Divorced' },
                  { value: 'Widowed', label: 'Widowed' },
                ]}
              />
              <FieldRow label="Dependents" error={errors.dependents?.message}>
                <Input type="number" {...register('dependents')} min={0} max={10} />
              </FieldRow>
              <SelectField
                label="Location Type"
                value={values.location || ''}
                onChange={(v) => setValue('location', v)}
                error={errors.location?.message}
                options={[
                  { value: 'Urban', label: 'Urban (Metro / Large City)' },
                  { value: 'Semi-Urban', label: 'Semi-Urban (Tier 2/3 City)' },
                  { value: 'Rural', label: 'Rural (Town / Village)' },
                ]}
              />
              <SelectField
                label="Employment Type"
                value={values.employment_type || ''}
                onChange={(v) => setValue('employment_type', v)}
                error={errors.employment_type?.message}
                options={[
                  { value: 'Full-Time', label: 'Full-Time' },
                  { value: 'Part-Time', label: 'Part-Time' },
                  { value: 'Contract', label: 'Contract / Gig' },
                  { value: 'Unemployed', label: 'Unemployed' },
                ]}
              />
              <FieldRow label="Years of Experience" error={errors.years_of_experience?.message}>
                <Input type="number" {...register('years_of_experience')} />
              </FieldRow>
            </CardContent>
          </Card>
        )}

        {/* Step 1: Financial Profile */}
        {step === 1 && (
          <Card>
            <CardHeader>
              <CardTitle>Financial Profile</CardTitle>
              <CardDescription>Your financial situation and habits</CardDescription>
            </CardHeader>
            <CardContent className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <FieldRow label="Monthly Income (₹)" error={errors.monthly_income?.message}>
                <Input type="number" {...register('monthly_income')} />
              </FieldRow>
              <FieldRow label="Monthly Expenses (₹)" error={errors.monthly_expenses?.message}>
                <Input type="number" {...register('monthly_expenses')} />
              </FieldRow>
              <FieldRow label="Savings Rate (%)" error={errors.savings_rate?.message}>
                <Input type="number" {...register('savings_rate')} min={0} max={100} />
              </FieldRow>
              <FieldRow label="Emergency Fund (months)" error={errors.emergency_fund_months?.message}>
                <Input type="number" {...register('emergency_fund_months')} />
              </FieldRow>
              <FieldRow label="Total Debt (₹)" error={errors.total_debt?.message}>
                <Input type="number" {...register('total_debt')} />
              </FieldRow>
              <FieldRow label="Loan Amount (₹)" error={errors.loan_amount?.message}>
                <Input type="number" {...register('loan_amount')} />
              </FieldRow>
              <FieldRow label="Credit Score (300-900)" error={errors.credit_score?.message}>
                <Input type="number" {...register('credit_score')} min={300} max={900} />
              </FieldRow>
              <FieldRow label="Investment Experience (years)" error={errors.investment_experience_years?.message}>
                <Input type="number" {...register('investment_experience_years')} />
              </FieldRow>
              <SelectField
                label="Investment Frequency"
                value={values.investment_frequency || ''}
                onChange={(v) => setValue('investment_frequency', v)}
                error={errors.investment_frequency?.message}
                options={[
                  { value: 'Never', label: 'Never' },
                  { value: 'Rarely', label: 'Rarely (a few times a year)' },
                  { value: 'Monthly', label: 'Monthly' },
                  { value: 'Weekly', label: 'Weekly' },
                ]}
              />
              <SelectField
                label="Insurance Coverage"
                value={values.insurance_coverage || ''}
                onChange={(v) => setValue('insurance_coverage', v)}
                error={errors.insurance_coverage?.message}
                options={[
                  { value: 'None', label: 'None' },
                  { value: 'Basic', label: 'Basic (Life / Health)' },
                  { value: 'Comprehensive', label: 'Comprehensive (Life + Health + Vehicle)' },
                ]}
              />
            </CardContent>
          </Card>
        )}

        {/* Step 2: Lifestyle */}
        {step === 2 && (
          <Card>
            <CardHeader>
              <CardTitle>Lifestyle</CardTitle>
              <CardDescription>Your spending patterns and lifestyle habits</CardDescription>
            </CardHeader>
            <CardContent className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <SelectField
                label="Shopping Frequency"
                value={values.shopping_frequency || ''}
                onChange={(v) => setValue('shopping_frequency', v)}
                error={errors.shopping_frequency?.message}
                options={[
                  { value: 'Rarely', label: 'Rarely' },
                  { value: 'Monthly', label: 'Monthly' },
                  { value: 'Weekly', label: 'Weekly' },
                  { value: 'Daily', label: 'Daily' },
                ]}
              />
              <FieldRow label="Online Spending (%)" error={errors.online_spending_pct?.message}>
                <Input type="number" {...register('online_spending_pct')} min={0} max={100} />
              </FieldRow>
              <FieldRow label="Luxury Spending (%)" error={errors.luxury_spending_pct?.message}>
                <Input type="number" {...register('luxury_spending_pct')} min={0} max={100} />
              </FieldRow>
              <FieldRow label="Active Subscriptions" error={errors.subscription_count?.message}>
                <Input type="number" {...register('subscription_count')} />
              </FieldRow>
              <FieldRow label="Gaming Expenses/Month (₹)" error={errors.gaming_expenses_monthly?.message}>
                <Input type="number" {...register('gaming_expenses_monthly')} />
              </FieldRow>
              <FieldRow label="Travel Expenses/Year (₹)" error={errors.travel_expenses_annual?.message}>
                <Input type="number" {...register('travel_expenses_annual')} />
              </FieldRow>
            </CardContent>
          </Card>
        )}

        {/* Step 3: Review */}
        {step === 3 && (
          <Card>
            <CardHeader>
              <CardTitle>Review & Submit</CardTitle>
              <CardDescription>Please review your information before submitting</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <ReviewSection title="Demographics">
                <ReviewItem label="Age" value={values.age} />
                <ReviewItem label="Gender" value={values.gender} />
                <ReviewItem label="Education" value={values.education} />
                <ReviewItem label="Occupation" value={values.occupation} />
                <ReviewItem label="Income Level" value={values.income_level} />
                <ReviewItem label="Marital Status" value={values.marital_status} />
                <ReviewItem label="Dependents" value={values.dependents} />
                <ReviewItem label="Location" value={values.location} />
                <ReviewItem label="Employment Type" value={values.employment_type} />
                <ReviewItem label="Years of Experience" value={values.years_of_experience} />
              </ReviewSection>

              <ReviewSection title="Financial Profile">
                <ReviewItem label="Monthly Income" value={`₹${values.monthly_income?.toLocaleString()}`} />
                <ReviewItem label="Monthly Expenses" value={`₹${values.monthly_expenses?.toLocaleString()}`} />
                <ReviewItem label="Savings Rate" value={`${values.savings_rate}%`} />
                <ReviewItem label="Emergency Fund" value={`${values.emergency_fund_months} months`} />
                <ReviewItem label="Credit Score" value={values.credit_score} />
                <ReviewItem label="Investment Frequency" value={values.investment_frequency} />
                <ReviewItem label="Insurance" value={values.insurance_coverage} />
              </ReviewSection>

              <ReviewSection title="Lifestyle">
                <ReviewItem label="Shopping Frequency" value={values.shopping_frequency} />
                <ReviewItem label="Online Spending" value={`${values.online_spending_pct}%`} />
                <ReviewItem label="Luxury Spending" value={`${values.luxury_spending_pct}%`} />
                <ReviewItem label="Subscriptions" value={values.subscription_count} />
                <ReviewItem label="Gaming/Month" value={`₹${values.gaming_expenses_monthly?.toLocaleString()}`} />
                <ReviewItem label="Travel/Year" value={`₹${values.travel_expenses_annual?.toLocaleString()}`} />
              </ReviewSection>

              {error && (
                <div className="p-3 rounded-md bg-destructive/10 text-destructive text-sm">
                  {error}
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Navigation */}
        <div className="flex justify-between mt-6">
          <Button type="button" variant="outline" onClick={prevStep} disabled={step === 0}>
            <ChevronLeft className="h-4 w-4 mr-1" /> Back
          </Button>
          {step < STEPS.length - 1 ? (
            <Button type="button" onClick={nextStep}>
              Next <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          ) : (
            <Button type="submit" disabled={isSubmitting} className="gap-2">
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <CheckCircle className="h-4 w-4" />
                  Submit Assessment
                </>
              )}
            </Button>
          )}
        </div>
      </form>
    </div>
  )
}

function ReviewSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h3 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide mb-3">{title}</h3>
      <div className="grid grid-cols-2 gap-2">{children}</div>
    </div>
  )
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function ReviewItem({ label, value }: { label: string; value: any }) {
  return (
    <div className="flex flex-col">
      <span className="text-xs text-muted-foreground">{label}</span>
      <span className="text-sm font-medium">{value ?? '—'}</span>
    </div>
  )
}
