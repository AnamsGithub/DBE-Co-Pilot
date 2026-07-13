import React from 'react'
import { useNavigate } from 'react-router-dom'

export default function Landing() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <nav className="bg-white border-b px-8 py-4 flex items-center justify-between">
        <button
          onClick={() => navigate('/')}
          className="text-xl font-bold text-blue-600 hover:opacity-80 transition-opacity"
        >
          DBECopilot AI
        </button>
        <button
          onClick={() => navigate('/upload')}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
        >
          Get Started
        </button>
      </nav>

      <main className="flex-1 flex flex-col items-center justify-center px-4 text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          AI-Powered Placement Advisor
          <br />
          <span className="text-blue-600">for MBA Students</span>
        </h1>
        <p className="text-gray-500 text-lg max-w-xl mb-8">
          Upload your resume, pick your target, and get an instant career report with resume score, company matches, skill gaps, and a personalised improvement plan.
        </p>
        <button
          onClick={() => navigate('/upload')}
          className="bg-blue-600 text-white px-8 py-3 rounded-lg text-base font-semibold hover:bg-blue-700"
        >
          Analyse My Resume
        </button>

        <div className="mt-16 grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-3xl w-full">
          {[
            { title: 'Resume Score', desc: 'Honest quality score out of 100 based on your target' },
            { title: 'Company Match', desc: 'See which companies fit your profile and by how much' },
            { title: 'Skill Roadmap', desc: '4-week personalised plan to close your skill gaps' },
          ].map((f) => (
            <div key={f.title} className="bg-white border rounded-xl p-5 text-left shadow-sm">
              <h3 className="font-semibold text-gray-800 mb-1">{f.title}</h3>
              <p className="text-sm text-gray-500">{f.desc}</p>
            </div>
          ))}
        </div>
      </main>
    </div>
  )
}
