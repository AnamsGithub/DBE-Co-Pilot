import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

export async function uploadResume(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await api.post('/api/resume/upload', form)
  return res.data
}

export async function analyzeResume(sessionId, targetType, targetValue) {
  const res = await api.post('/api/career/analyze', {
    session_id: sessionId,
    target_type: targetType,
    target_value: targetValue,
  })
  return res.data
}

export async function checkCV(sessionId, filename) {
  const res = await api.post('/api/career/check-cv', {
    session_id: sessionId,
    filename: filename,
  })
  return res.data
}

export async function getCompanies() {
  const res = await api.get('/api/career/companies')
  return res.data
}

export function downloadUrl(filename) {
  const base = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  return `${base}/api/career/download/${filename}`
}
