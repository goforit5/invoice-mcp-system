import React, { useState } from 'react'
import DragDrop from './components/DragDrop'
import ReviewPage from './components/ReviewPage'
import DatabaseView from './components/DatabaseView'

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
        <DragDrop 
          onProcessingComplete={handleProcessingComplete}
          onViewDatabase={handleViewDatabase}
        />
      )}
      
      {currentView === 'review' && processingResult && (
        <ReviewPage 
          result={processingResult} 
          onBack={handleBackToUpload}
        />
      )}

      {currentView === 'database' && (
        <DatabaseView 
          onBack={handleBackToUpload}
          onViewRecord={handleViewRecord}
        />
      )}
    </div>
  )
}

export default App