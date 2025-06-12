import React, { useState, useEffect } from 'react'

const AgenticWorkflow = ({ workflowData, onBack, onViewCRM }) => {
  const [activeWorkflows, setActiveWorkflows] = useState([])
  const [workflowHistory, setWorkflowHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedWorkflow, setSelectedWorkflow] = useState(null)

  // Sample workflow templates
  const WORKFLOW_TEMPLATES = [
    {
      id: 'invoice_processing',
      name: 'Invoice Processing',
      description: 'Automatically process invoices through QuickBooks integration',
      icon: '🧾',
      color: 'blue',
      steps: [
        'Extract vendor information',
        'Match with existing QuickBooks vendors',
        'Automatically code line items',
        'Post to QuickBooks',
        'Create follow-up tasks'
      ],
      triggers: ['Document Type: Invoice', 'Keywords: bill, payment due, invoice']
    },
    {
      id: 'dmv_processing',
      name: 'DMV Document Processing',
      description: 'Handle motor vehicle documents and create urgent tasks',
      icon: '🚗',
      color: 'red',
      steps: [
        'Classify DMV document type',
        'Extract key information (license, dates)',
        'Create urgent task for action required',
        'Link to DMV company record',
        'Set follow-up reminders'
      ],
      triggers: ['Document Type: DMV', 'Keywords: motor vehicles, license, registration']
    },
    {
      id: 'medical_processing',
      name: 'Medical Document Processing',
      description: 'Process medical bills and health documents',
      icon: '🏥',
      color: 'green',
      steps: [
        'Extract patient and provider information',
        'Identify insurance information',
        'Calculate patient responsibility',
        'Create payment tracking task',
        'Link to healthcare provider'
      ],
      triggers: ['Document Type: Medical', 'Keywords: patient, medical, clinic']
    },
    {
      id: 'financial_processing',
      name: 'Financial Statement Processing',
      description: 'Analyze brokerage statements and investment documents',
      icon: '📊',
      color: 'purple',
      steps: [
        'Extract account information',
        'Analyze portfolio holdings',
        'Calculate performance metrics',
        'Create investment review task',
        'Update financial records'
      ],
      triggers: ['Document Type: Brokerage', 'Keywords: portfolio, investment, statement']
    },
    {
      id: 'legal_processing',
      name: 'Legal Notice Processing',
      description: 'Handle legal documents and court notices',
      icon: '⚖️',
      color: 'yellow',
      steps: [
        'Classify legal document type',
        'Extract case information',
        'Identify important dates',
        'Create high-priority tasks',
        'Set court date reminders'
      ],
      triggers: ['Document Type: Legal', 'Keywords: court, legal, notice']
    }
  ]

  useEffect(() => {
    loadWorkflowData()
  }, [])

  const loadWorkflowData = async () => {
    try {
      // Simulate loading workflow data
      setLoading(true)
      
      // Mock active workflows
      const mockActiveWorkflows = [
        {
          id: 'wf_001',
          template: 'medical_processing',
          status: 'running',
          progress: 75,
          document: 'Coastal Kids Medical Bill',
          startTime: new Date(Date.now() - 1000 * 60 * 5), // 5 minutes ago
          currentStep: 'Create payment tracking task',
          completedSteps: 3,
          totalSteps: 5
        },
        {
          id: 'wf_002',
          template: 'invoice_processing',
          status: 'completed',
          progress: 100,
          document: 'Office Supplies Invoice',
          startTime: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
          completedSteps: 5,
          totalSteps: 5
        }
      ]

      // Mock workflow history
      const mockHistory = [
        {
          id: 'wf_003',
          template: 'dmv_processing',
          status: 'completed',
          document: 'Vehicle Registration Notice',
          startTime: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
          endTime: new Date(Date.now() - 1000 * 60 * 60 * 2 + 1000 * 60 * 3), // 3 minutes later
          outcome: 'Created urgent task for license renewal',
          completedSteps: 5,
          totalSteps: 5
        },
        {
          id: 'wf_004',
          template: 'financial_processing',
          status: 'completed',
          document: 'Fidelity Statement Q3 2024',
          startTime: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
          endTime: new Date(Date.now() - 1000 * 60 * 60 * 24 + 1000 * 60 * 8), // 8 minutes later
          outcome: 'Portfolio analysis complete, created review task',
          completedSteps: 5,
          totalSteps: 5
        }
      ]

      setActiveWorkflows(mockActiveWorkflows)
      setWorkflowHistory(mockHistory)
    } catch (error) {
      console.error('Failed to load workflow data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getWorkflowTemplate = (templateId) => {
    return WORKFLOW_TEMPLATES.find(t => t.id === templateId) || WORKFLOW_TEMPLATES[0]
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return 'bg-blue-100 text-blue-800'
      case 'completed': return 'bg-green-100 text-green-800'
      case 'failed': return 'bg-red-100 text-red-800'
      case 'paused': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const formatDuration = (startTime, endTime = new Date()) => {
    const duration = Math.floor((endTime - new Date(startTime)) / 1000)
    if (duration < 60) return `${duration}s`
    if (duration < 3600) return `${Math.floor(duration / 60)}m ${duration % 60}s`
    return `${Math.floor(duration / 3600)}h ${Math.floor((duration % 3600) / 60)}m`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-green-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">🤖 AI Workflow Engine</h2>
          <p className="text-gray-600 mt-2">Intelligent automation for document processing workflows</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={onViewCRM}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            👥 View CRM
          </button>
          <button
            onClick={onBack}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            ← Back to Processor
          </button>
        </div>
      </div>

      {/* Workflow Stats */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Workflow Statistics</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{activeWorkflows.length}</div>
            <div className="text-sm text-gray-600">Active Workflows</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{workflowHistory.length}</div>
            <div className="text-sm text-gray-600">Completed Today</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">{WORKFLOW_TEMPLATES.length}</div>
            <div className="text-sm text-gray-600">Available Templates</div>
          </div>
          <div className="text-center p-4 bg-yellow-50 rounded-lg">
            <div className="text-2xl font-bold text-yellow-600">98%</div>
            <div className="text-sm text-gray-600">Success Rate</div>
          </div>
        </div>
      </div>

      {/* Active Workflows */}
      {activeWorkflows.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">⚡ Active Workflows</h3>
          <div className="space-y-4">
            {activeWorkflows.map((workflow) => {
              const template = getWorkflowTemplate(workflow.template)
              return (
                <div key={workflow.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`text-2xl p-2 rounded-lg bg-${template.color}-100`}>
                        {template.icon}
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900">{template.name}</h4>
                        <p className="text-sm text-gray-600">Processing: {workflow.document}</p>
                        <p className="text-xs text-gray-500">Started {formatDuration(workflow.startTime)} ago</p>
                      </div>
                    </div>
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(workflow.status)}`}>
                      {workflow.status}
                    </span>
                  </div>
                  
                  {/* Progress Bar */}
                  <div className="mt-4">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">
                        {workflow.currentStep || `Step ${workflow.completedSteps} of ${workflow.totalSteps}`}
                      </span>
                      <span className="text-gray-600">{workflow.progress}%</span>
                    </div>
                    <div className="mt-2 bg-gray-200 rounded-full h-2">
                      <div 
                        className={`bg-${template.color}-500 h-2 rounded-full transition-all duration-500`}
                        style={{ width: `${workflow.progress}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Current Step Details */}
                  {workflow.status === 'running' && (
                    <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                      <p className="text-sm text-blue-800">
                        🔄 Currently: {workflow.currentStep}
                      </p>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Workflow Templates */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🛠️ Available Workflow Templates</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {WORKFLOW_TEMPLATES.map((template) => (
            <div 
              key={template.id} 
              className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 hover:shadow-sm transition-all cursor-pointer"
              onClick={() => setSelectedWorkflow(template)}
            >
              <div className="flex items-start space-x-3">
                <div className={`text-2xl p-2 rounded-lg bg-${template.color}-100`}>
                  {template.icon}
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{template.name}</h4>
                  <p className="text-sm text-gray-600 mt-1">{template.description}</p>
                  <div className="mt-2">
                    <p className="text-xs text-gray-500 font-medium">Triggers:</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {template.triggers.slice(0, 2).map((trigger, index) => (
                        <span key={index} className="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded">
                          {trigger}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Workflow History */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📋 Recent Workflow History</h3>
        <div className="space-y-3">
          {workflowHistory.map((workflow) => {
            const template = getWorkflowTemplate(workflow.template)
            return (
              <div key={workflow.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`text-lg p-2 rounded bg-${template.color}-100`}>
                    {template.icon}
                  </div>
                  <div>
                    <h5 className="font-medium text-gray-900">{template.name}</h5>
                    <p className="text-sm text-gray-600">{workflow.document}</p>
                    <p className="text-xs text-gray-500">
                      {formatDuration(workflow.startTime, workflow.endTime)} • {workflow.outcome}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(workflow.status)}`}>
                    {workflow.status}
                  </span>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(workflow.startTime).toLocaleString()}
                  </p>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Workflow Detail Modal */}
      {selectedWorkflow && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full mx-4 max-h-screen overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className={`text-3xl p-3 rounded-lg bg-${selectedWorkflow.color}-100`}>
                    {selectedWorkflow.icon}
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900">{selectedWorkflow.name}</h3>
                    <p className="text-gray-600">{selectedWorkflow.description}</p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedWorkflow(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Workflow Steps</h4>
                  <div className="space-y-2">
                    {selectedWorkflow.steps.map((step, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <div className={`w-6 h-6 rounded-full bg-${selectedWorkflow.color}-100 text-${selectedWorkflow.color}-600 flex items-center justify-center text-xs font-medium`}>
                          {index + 1}
                        </div>
                        <span className="text-sm text-gray-700">{step}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Trigger Conditions</h4>
                  <div className="space-y-1">
                    {selectedWorkflow.triggers.map((trigger, index) => (
                      <div key={index} className="text-sm text-gray-600">
                        • {trigger}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default AgenticWorkflow