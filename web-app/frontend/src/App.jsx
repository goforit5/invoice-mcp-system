import React, { useState } from 'react'
import MCPProcessor from './components/MCPProcessor'
import DocumentReview from './components/DocumentReview'
import CRMDashboard from './components/CRMDashboard'
import AgenticWorkflow from './components/AgenticWorkflow'

function App() {
  const [currentView, setCurrentView] = useState('processor') // 'processor', 'review', 'crm', 'workflow'
  const [processingResult, setProcessingResult] = useState(null)
  const [workflowData, setWorkflowData] = useState(null)

  const handleProcessingComplete = (result) => {
    setProcessingResult(result)
    setCurrentView('review')
  }

  const handleWorkflowTriggered = (workflowData) => {
    setWorkflowData(workflowData)
    // Stay on current view but show workflow status
  }

  const handleViewCRM = () => {
    setCurrentView('crm')
  }

  const handleViewWorkflow = () => {
    setCurrentView('workflow')
  }

  const handleBackToProcessor = () => {
    setCurrentView('processor')
    setProcessingResult(null)
    setWorkflowData(null)
  }

  const handleViewRecord = (result) => {
    setProcessingResult(result)
    setCurrentView('review')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Navigation Header */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  📄 Universal Document AI
                </h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setCurrentView('processor')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  currentView === 'processor'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                🤖 MCP Processor
              </button>
              <button
                onClick={handleViewCRM}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  currentView === 'crm'
                    ? 'bg-purple-100 text-purple-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                👥 CRM Dashboard
              </button>
              <button
                onClick={handleViewWorkflow}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  currentView === 'workflow'
                    ? 'bg-green-100 text-green-700'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                }`}
              >
                🤖 AI Workflows
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'processor' && (
          <MCPProcessor 
            onProcessingComplete={handleProcessingComplete}
          />
        )}
        
        {currentView === 'review' && processingResult && (
          <DocumentReview 
            result={processingResult} 
            onBack={handleBackToProcessor}
            onViewCRM={handleViewCRM}
            onViewWorkflow={handleViewWorkflow}
          />
        )}

        {currentView === 'crm' && (
          <CRMDashboard 
            onBack={handleBackToProcessor}
            onViewRecord={handleViewRecord}
            onViewWorkflow={handleViewWorkflow}
          />
        )}

        {currentView === 'workflow' && (
          <AgenticWorkflow 
            workflowData={workflowData}
            onBack={handleBackToProcessor}
            onViewCRM={handleViewCRM}
          />
        )}
      </div>
    </div>
  )
}

export default App