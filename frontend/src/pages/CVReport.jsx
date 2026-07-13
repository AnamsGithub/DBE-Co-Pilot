import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

export default function CVReport() {
  const { state } = useLocation()
  const navigate = useNavigate()

  if (!state?.report) { navigate('/'); return null }

  const { report } = state
  const { student_name, filename_ok, compliance_issues, pointer_improvements } = report

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
          Check another CV
        </button>
      </nav>

      <div className="max-w-4xl mx-auto px-4 py-8 space-y-6">

        {/* Header */}
        <div className="bg-white border rounded-xl p-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{student_name}</h1>
            <p className="text-sm text-gray-500 mt-1">DBE-DU CV Format Check</p>
          </div>
          <span className={`text-sm font-medium px-3 py-1 rounded-full ${compliance_issues.length === 0 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
            {compliance_issues.length === 0 ? 'Format looks good' : `${compliance_issues.length} issue${compliance_issues.length > 1 ? 's' : ''} to fix`}
          </span>
        </div>

        {/* Compliance Issues */}
        {compliance_issues.length > 0 && (
          <div className="bg-white border rounded-xl p-5">
            <h2 className="font-semibold text-gray-800 mb-1">Format Issues</h2>
            <p className="text-xs text-gray-400 mb-4">These need to be fixed before submitting your CV.</p>
            <div className="space-y-3">
              {compliance_issues.map((issue, i) => (
                <div key={i} className="border border-red-100 bg-red-50 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium bg-red-100 text-red-700 px-2 py-0.5 rounded">{issue.section}</span>
                  </div>
                  <p className="text-sm text-red-700">{issue.issue}</p>
                  <p className="text-sm text-green-700 mt-1">Fix: {issue.suggestion}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Pointer Improvements */}
        {pointer_improvements.length > 0 ? (
          <div className="bg-white border rounded-xl p-5">
            <h2 className="font-semibold text-gray-800 mb-1">Bullet Point Improvements</h2>
            <p className="text-xs text-gray-400 mb-4">
              Bullets that were too short have been expanded. Structural parts (name, dates, headers, education) are not touched.
            </p>
            <div className="space-y-5">
              {pointer_improvements.map((imp, i) => (
                <div key={i} className="space-y-1">
                  <p className="text-xs text-gray-400">{imp.section}</p>
                  <div className="flex gap-2 items-start">
                    <span className="text-xs text-red-400 font-semibold mt-0.5 shrink-0 w-12">Before</span>
                    <p className="text-sm text-gray-500 bg-gray-50 rounded px-2 py-1 flex-1">
                      {imp.original}
                      <span className="text-xs text-gray-300 ml-2">{imp.original.length} chars</span>
                    </p>
                  </div>
                  <div className="flex gap-2 items-start">
                    <span className="text-xs text-green-600 font-semibold mt-0.5 shrink-0 w-12">After</span>
                    <p className="text-sm text-gray-700 bg-green-50 rounded px-2 py-1 flex-1">
                      {imp.improved}
                      <span className="text-xs text-gray-400 ml-2">{imp.improved.length} chars</span>
                    </p>
                  </div>
                  <p className="text-xs text-gray-400 pl-14">{imp.reason}</p>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="bg-green-50 border border-green-200 rounded-xl p-5 text-center">
            <p className="text-green-700 font-medium">All bullet points are the right length</p>
            <p className="text-sm text-green-600 mt-1">Nothing to improve here</p>
          </div>
        )}

      </div>
    </div>
  )
}
