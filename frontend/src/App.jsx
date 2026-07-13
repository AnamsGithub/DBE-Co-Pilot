import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import Upload from './pages/Upload'
import Dashboard from './pages/Dashboard'
import CVReport from './pages/CVReport'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/upload" element={<Upload />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/cv-report" element={<CVReport />} />
    </Routes>
  )
}
