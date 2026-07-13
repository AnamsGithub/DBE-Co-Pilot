import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadResume, analyzeResume, checkCV, getCompanies } from '../api/client'

const ROLES = ['Business Analyst', 'Product Manager', 'Marketing Analyst', 'Finance Analyst', 'Consultant']
const CTC_OPTIONS = ['Below 12 LPA', '12 to 15 LPA', 'Above 15 LPA']

const TARGET_TYPES = [
  { key: 'role',    label: 'Target Role',    hint: 'Select the role you are applying for' },
  { key: 'company', label: 'Target Company', hint: 'Select the company you are aiming for' },
  { key: 'ctc',     label: 'Target CTC',     hint: 'Select your target CTC range' },
  { key: 'all',     label: 'All Companies',  hint: 'Analyse broadly across all placement roles' },
]

export default function Upload() {
  const navigate = useNavigate()
  const [tab, setTab] = useState('career')
  const [file, setFile] = useState(null)
  const [targetType, setTargetType] = useState('role')
  const [targetValue, setTargetValue] = useState('')
  const [status, setStatus] = useState('idle')
  const [error, setError] = useState('')
  const [companies, setCompanies] = useState([])

  useEffect(() => {
    getCompanies().then(setCompanies).catch(() => {})
  }, [])

  function resetForm(newTab) {
    setTab(newTab)
    setFile(null)
    setTargetType('role')
    setTargetValue('')
    setStatus('idle')
    setError('')
  }

  function isReadyToAnalyse() {
    if (!file) return false
    if (targetType === 'all') return true
    return targetValue.trim().length > 0
  }

  async function handleCareerSubmit(e) {
    e.preventDefault()
    if (!isReadyToAnalyse()) return
    try {
      setStatus('uploading')
      const { session_id } = await uploadResume(file)
      setStatus('analysing')
      const report = await analyzeResume(session_id, targetType, targetValue)
      navigate('/dashboard', { state: { report, targetType, targetValue, sessionId: session_id, filename: file.name } })
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong.')
      setStatus('error')
    }
  }

  async function handleCVSubmit(e) {
    e.preventDefault()
    if (!file) return
    try {
      setStatus('uploading')
      const { session_id } = await uploadResume(file)
      setStatus('analysing')
      const report = await checkCV(session_id, file.name)
      navigate('/cv-report', { state: { report } })
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong.')
      setStatus('error')
    }
  }

  const busy = status === 'uploading' || status === 'analysing'

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <nav className="bg-white border-b px-8 py-4">
        <button
          onClick={() => navigate('/')}
          className="text-xl font-bold text-blue-600 hover:opacity-80 transition-opacity"
        >
          DBECopilot AI
        </button>
      </nav>

      <div className="flex-1 flex items-center justify-center px-4 py-8">
        <div className="bg-white border rounded-xl shadow-sm p-8 w-full max-w-md">

          {/* Tabs */}
          <div className="flex border-b mb-6">
            {[['career', 'Career Analysis'], ['cv', 'CV Format Check']].map(([key, label]) => (
              <button
                key={key}
                onClick={() => resetForm(key)}
                className={`flex-1 pb-2 text-sm font-medium border-b-2 transition-colors ${tab === key ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-400 hover:text-gray-600'}`}
              >
                {label}
              </button>
            ))}
          </div>

          {tab === 'career' ? (
            <form onSubmit={handleCareerSubmit} className="space-y-5">
              <h2 className="text-xl font-bold text-gray-900">Analyse Your Resume</h2>
              <FileInput file={file} setFile={setFile} />

              {/* Target type selector */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">What are you targeting?</label>
                <div className="grid grid-cols-2 gap-2">
                  {TARGET_TYPES.map(({ key, label }) => (
                    <button
                      key={key}
                      type="button"
                      onClick={() => { setTargetType(key); setTargetValue('') }}
                      className={`py-2 px-3 rounded-lg text-sm font-medium border transition-colors text-left ${
                        targetType === key
                          ? 'bg-blue-600 text-white border-blue-600'
                          : 'bg-white text-gray-600 border-gray-200 hover:border-blue-300'
                      }`}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Target value input */}
              {targetType !== 'all' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {TARGET_TYPES.find(t => t.key === targetType)?.hint}
                  </label>
                  <select
                    value={targetValue}
                    onChange={(e) => setTargetValue(e.target.value)}
                    className="w-full border rounded-lg px-3 py-2 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Select...</option>
                    {targetType === 'role' && ROLES.map((r) => <option key={r}>{r}</option>)}
                    {targetType === 'company' && companies.map((c) => <option key={c}>{c}</option>)}
                    {targetType === 'ctc' && CTC_OPTIONS.map((c) => <option key={c}>{c}</option>)}
                  </select>
                </div>
              )}

              {targetType === 'all' && (
                <p className="text-xs text-gray-400">
                  Your resume will be assessed against all company types in our database.
                </p>
              )}

              <StatusMessage status={status} error={error} />
              <button
                type="submit"
                disabled={!isReadyToAnalyse() || busy}
                className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-semibold text-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {busy ? 'Processing...' : 'Analyse Resume'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleCVSubmit} className="space-y-5">
              <h2 className="text-xl font-bold text-gray-900">Check CV Format</h2>
              <p className="text-sm text-gray-500">Checks DBE-DU guidelines compliance and improves bullet point length.</p>
              <FileInput file={file} setFile={setFile} />
              <StatusMessage status={status} error={error} />
              <button
                type="submit"
                disabled={!file || busy}
                className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-semibold text-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {busy ? 'Processing...' : 'Check CV'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}

function FileInput({ file, setFile }) {
  return (
    <label className="block border-2 border-dashed border-gray-300 rounded-lg p-6 text-center cursor-pointer hover:border-blue-400 transition-colors">
      <input type="file" accept=".pdf" className="hidden" onChange={(e) => setFile(e.target.files[0])} />
      {file
        ? <span className="text-blue-600 font-medium">{file.name}</span>
        : <span className="text-gray-400 text-sm">Click to select a PDF</span>}
    </label>
  )
}

function StatusMessage({ status, error }) {
  if (status === 'error') return <p className="text-sm text-red-500">{error}</p>
  if (status === 'uploading') return <p className="text-sm text-blue-600 text-center">Uploading...</p>
  if (status === 'analysing') return <p className="text-sm text-blue-600 text-center">Analysing with AI, about 20 seconds...</p>
  return null
}
