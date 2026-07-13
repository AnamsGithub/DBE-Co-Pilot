import React, { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { checkCV } from '../api/client'

export default function Dashboard() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const [cvChecking, setCvChecking] = useState(false)

  if (!state?.report) {
    navigate('/')
    return null
  }

  const { report, targetType, targetValue, sessionId, filename } = state
  const { resume_data, analysis, skill_roadmap } = report
  const company_matches = (targetType === 'company'
    ? report.company_matches.filter(c => c.company_name.toLowerCase() === targetValue.toLowerCase())
    : report.company_matches
  ).slice().sort((a, b) => b.match_score - a.match_score)

  const scoreColor =
    analysis.score >= 80 ? 'text-green-600' :
    analysis.score >= 60 ? 'text-yellow-500' : 'text-red-500'

  const targetLabel = {
    role:    `Target Role: ${targetValue}`,
    company: `Target Company: ${targetValue}`,
    ctc:     `Target CTC: ${targetValue}`,
    all:     'Analysed across all companies',
  }[targetType] || targetValue

  async function handleViewCVErrors() {
    if (!sessionId) { navigate('/upload'); return }
    try {
      setCvChecking(true)
      const cvReport = await checkCV(sessionId, filename || '')
      navigate('/cv-report', { state: { report: cvReport } })
    } catch {
      navigate('/upload')
    } finally {
      setCvChecking(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b px-8 py-4 flex items-center justify-between">
        <button
          onClick={() => navigate('/')}
          className="text-xl font-bold text-blue-600 hover:opacity-80 transition-opacity"
        >
          DBECopilot AI
        </button>
        <button onClick={() => navigate('/upload')} className="text-sm text-blue-600 hover:underline">
          Analyse another resume
        </button>
      </nav>

      <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">

        {/* Score card */}
        <div className="bg-white border rounded-xl p-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{resume_data.name}</h1>
            <p className="text-gray-500 text-sm mt-1">{targetLabel}</p>
          </div>
          <div className="text-center">
            <p className={`text-5xl font-bold ${scoreColor}`}>{analysis.score}</p>
            <p className="text-xs text-gray-400 mt-1">Resume Score / 100</p>
          </div>
        </div>

        {/* Strengths and Weaknesses */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="bg-white border rounded-xl p-5">
            <h2 className="font-semibold text-gray-800 mb-3">Strengths</h2>
            <ul className="space-y-1">
              {analysis.strengths.map((s, i) => (
                <li key={i} className="text-sm text-gray-600 flex gap-2">
                  <span className="text-green-500 shrink-0">+</span> {s}
                </li>
              ))}
            </ul>
          </div>
          <div className="bg-white border rounded-xl p-5">
            <h2 className="font-semibold text-gray-800 mb-3">Weaknesses</h2>
            <ul className="space-y-1">
              {analysis.weaknesses.map((w, i) => (
                <li key={i} className="text-sm text-gray-600 flex gap-2">
                  <span className="text-red-400 shrink-0">x</span> {w}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* DBE CV Format note */}
        <div className="bg-blue-50 border border-blue-100 rounded-xl p-5 flex items-center justify-between gap-4">
          <div>
            <h2 className="font-semibold text-blue-800 mb-1">DBE CV Format</h2>
            <p className="text-sm text-blue-700">
              Check if your CV follows the DBE-DU Excel template — correct date formats, bullet lengths, and section headers.
            </p>
          </div>
          <button
            onClick={handleViewCVErrors}
            disabled={cvChecking}
            className="shrink-0 text-sm font-medium text-blue-600 border border-blue-300 rounded-lg px-3 py-2 hover:bg-blue-100 transition-colors disabled:opacity-50"
          >
            {cvChecking ? 'Checking...' : 'View errors in detail'}
          </button>
        </div>

        {/* Company Matches */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-semibold text-gray-800 mb-4">Company Matches</h2>
          <div className="space-y-3">
            {company_matches.map((c, i) => (
              <div key={i} className="flex items-center gap-4">
                <div className="w-36 shrink-0">
                  <p className="text-sm font-medium text-gray-800">{c.company_name}</p>
                  <p className="text-xs text-gray-400">{c.role}</p>
                </div>
                <div className="flex-1 bg-gray-100 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${c.match_score >= 75 ? 'bg-green-500' : c.match_score >= 55 ? 'bg-yellow-400' : 'bg-red-400'}`}
                    style={{ width: `${c.match_score}%` }}
                  />
                </div>
                <span className="text-sm font-semibold text-gray-700 w-10 text-right">{c.match_score}%</span>
              </div>
            ))}
          </div>
          <div className="mt-4 pt-4 border-t">
            <p className="text-xs font-medium text-gray-500 mb-2">Skills to add to your resume:</p>
            <div className="flex flex-wrap gap-2">
              {[...new Set(company_matches.flatMap(c => c.missing_skills))].slice(0, 8).map((skill, i) => (
                <span key={i} className="bg-red-50 text-red-600 text-xs px-2 py-1 rounded-full border border-red-100">{skill}</span>
              ))}
            </div>
          </div>
        </div>

        {/* 4-Week Roadmap */}
        <div className="bg-white border rounded-xl p-5">
          <h2 className="font-semibold text-gray-800 mb-1">Your 4-Week Plan</h2>
          <p className="text-xs text-gray-400 mb-5">One skill at a time. Each week has a project you can add to your resume.</p>
          <div className="space-y-5">
            {skill_roadmap.map((week, i) => (
              <WeekCard key={i} week={week} index={i} />
            ))}
          </div>
        </div>

      </div>
    </div>
  )
}

function WeekCard({ week, index }) {
  const [open, setOpen] = useState(index === 0)

  const focus   = week.focus   || week
  const advice  = week.advice  || ''
  const project = week.project || ''
  const label   = week.week    || `Week ${index + 1}`

  return (
    <div className="border rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-gray-50 transition-colors"
      >
        <span className="bg-blue-100 text-blue-700 text-xs font-bold px-2 py-1 rounded shrink-0">{label}</span>
        <span className="text-sm font-medium text-gray-800 flex-1">{focus}</span>
        <span className="text-gray-400 text-xs">{open ? 'hide' : 'show'}</span>
      </button>

      {open && (
        <div className="px-4 pb-4 space-y-3 border-t bg-gray-50">
          {advice && (
            <p className="text-sm text-gray-600 pt-3">{advice}</p>
          )}
          {project && (
            <div className="bg-white border border-blue-100 rounded-lg p-3">
              <p className="text-xs font-semibold text-blue-600 mb-1">Project idea</p>
              <p className="text-sm text-gray-700">{project}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
