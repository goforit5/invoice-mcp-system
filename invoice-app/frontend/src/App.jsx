import React, { useState } from 'react'
import InvoiceUpload from './components/InvoiceUpload'
import InvoiceReview from './components/InvoiceReview'
import InvoiceDatabase from './components/InvoiceDatabase'

function App() {
  const [currentView, setCurrentView] = useState('upload') // 'upload', 'review', or 'database'
  const [processingResult, setProcessingResult] = useState(null)

  const handleProcessingComplete = (result) => {
    setProcessingResult(result)
    setCurrentView('review')
  }

  const handleBackToUpload = () => {
    setCurrentView('upload')
    setProcessingResult(null)
  }

  const handleViewDatabase = () => {
    setCurrentView('database')
  }

  const handleViewRecord = (result) => {
    setProcessingResult(result)
    setCurrentView('review')
  }

  return (
    <div className="min-h-screen bg-white">
      {currentView === 'upload' && (
        <InvoiceUpload 
          onProcessingComplete={handleProcessingComplete}
          onViewDatabase={handleViewDatabase}
        />
      )}
      
      {currentView === 'review' && processingResult && (
        <InvoiceReview 
          result={processingResult} 
          onBack={handleBackToUpload}
        />
      )}

      {currentView === 'database' && (
        <InvoiceDatabase 
          onBack={handleBackToUpload}
          onViewRecord={handleViewRecord}
        />
      )}
    </div>
  )
}

export default App