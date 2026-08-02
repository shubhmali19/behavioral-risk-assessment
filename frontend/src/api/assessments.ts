// ============================================================
// SOURCE OF TRUTH: docs/api-contract.json
// All URLs, request shapes, and response unwrapping must match
// the contract. Do NOT change without updating api-contract.json.
// ============================================================

import client from './client'
import type {
  AssessmentInput,
  PredictionResponse,
  PredictionResult,
  AssessmentResponse,
  AssessmentsListResponse,
  AnalyticsResponse,
  HealthResponse,
  ModelInfoResponse,
} from '../types'

// POST /predict → { success, data: PredictionResult }
export async function postPredict(data: AssessmentInput): Promise<PredictionResult> {
  const response = await client.post<PredictionResponse>('/predict', data)
  return response.data.data
}

// POST /assessment → { success, assessment_id, data: PredictionResult }
export async function postAssessment(data: AssessmentInput): Promise<AssessmentResponse> {
  const response = await client.post<AssessmentResponse>('/assessment', data)
  return response.data
}

// GET /assessment/{id} → { success, assessment_id, data: PredictionResult }
export async function getAssessment(id: string): Promise<AssessmentResponse> {
  const response = await client.get<AssessmentResponse>(`/assessment/${id}`)
  return response.data
}

// GET /assessments?limit=&offset= → { success, total, items: AssessmentRecord[] }
export async function getAssessments(limit = 20, offset = 0): Promise<AssessmentsListResponse> {
  const response = await client.get<AssessmentsListResponse>('/assessments', {
    params: { limit, offset },
  })
  return response.data
}

// GET /analytics
export async function getAnalytics(): Promise<AnalyticsResponse> {
  const response = await client.get<AnalyticsResponse>('/analytics')
  return response.data
}

// GET /health
export async function getHealth(): Promise<HealthResponse> {
  const response = await client.get<HealthResponse>('/health')
  return response.data
}

// GET /model/info
export async function getModelInfo(): Promise<ModelInfoResponse> {
  const response = await client.get<ModelInfoResponse>('/model/info')
  return response.data
}
