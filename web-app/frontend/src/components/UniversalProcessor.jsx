import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'

const UniversalProcessor = ({ onProcessingComplete, onWorkflowTriggered, onViewCRM }) => {
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentStep, setCurrentStep] = useState(null)
  const [processingSteps, setProcessingSteps] = useState([])
  const [documentType, setDocumentType] = useState(null)
  const [uploadedFile, setUploadedFile] = useState(null)
  const [processedCount, setProcessedCount] = useState(0)

  // Processing steps configuration
  const PROCESSING_STEPS = [
    {
      id: 'upload',
      title: 'File Upload',
      description: 'Validating and uploading document',
      icon: '📤',
      color: 'blue'
    },
    {
      id: 'pdf_analysis',
      title: 'PDF Analysis',
      description: 'Converting pages to high-resolution images',
      icon: '🔍',
      color: 'indigo'
    },
    {
      id: 'ai_classification',
      title: 'AI Classification',
      description: 'Identifying document type using AI',
      icon: '🧠',
      color: 'purple'
    },
    {
      id: 'vision_extraction',
      title: 'Vision Extraction',
      description: 'Extracting text with OpenAI Vision API',
      icon: '👁️',
      color: 'green'
    },
    {
      id: 'structure_parsing',
      title: 'Structure Parsing',
      description: 'Converting to structured data',
      icon: '🏗️',
      color: 'yellow'
    },
    {
      id: 'crm_integration',
      title: 'CRM Integration',
      description: 'Creating contacts and communications',
      icon: '👥',
      color: 'pink'
    },
    {
      id: 'workflow_automation',
      title: 'Workflow Automation',
      description: 'Triggering AI-powered workflows',
      icon: '🤖',
      color: 'teal'
    },
    {
      id: 'complete',
      title: 'Complete',
      description: 'Document processing finished',
      icon: '✅',
      color: 'emerald'
    }
  ]

  // Document type configurations
  const DOCUMENT_TYPES = [
    { type: 'invoice', label: 'Invoice', icon: '🧾', description: 'Bills, invoices, medical statements' },
    { type: 'brokerage', label: 'Financial', icon: '📊', description: 'Brokerage statements, portfolios' },
    { type: 'dmv', label: 'DMV', icon: '🚗', description: 'Motor vehicle documents' },
    { type: 'legal', label: 'Legal', icon: '⚖️', description: 'Court documents, notices' },
    { type: 'medical', label: 'Medical', icon: '🏥', description: 'Health records, test results' },
    { type: 'tax', label: 'Tax', icon: '📋', description: 'Tax forms, 1099s, W-2s' },
    { type: 'general', label: 'General', icon: '📄', description: 'Other documents' }
  ]

  const updateStep = (stepId, status = 'active', details = {}) => {
    setCurrentStep(stepId)
    setProcessingSteps(prev => {
      const stepIndex = prev.findIndex(s => s.id === stepId)
      const step = PROCESSING_STEPS.find(s => s.id === stepId)
      
      const updatedStep = {
        ...step,
        status,
        timestamp: new Date(),
        ...details
      }

      if (stepIndex >= 0) {
        const newSteps = [...prev]
        newSteps[stepIndex] = updatedStep
        return newSteps
      } else {
        return [...prev, updatedStep]
      }
    })
  }

  const processDocument = async (file) => {
    setIsProcessing(true)
    setProcessingSteps([])
    setUploadedFile(file)
    
    try {
      updateStep('upload', 'active', { fileName: file.name, fileSize: `${(file.size / 1024 / 1024).toFixed(1)} MB` })

      const formData = new FormData()
      formData.append('pdf', file)

      // Start processing with streaming progress
      const response = await fetch('/api/universal-process', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        throw new Error('Processing failed')
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6)
            if (data === '[DONE]') {
              updateStep('complete', 'completed')
              setIsProcessing(false)
              setProcessedCount(prev => prev + 1)
              return
            }

            try {
              const progress = JSON.parse(data)
              handleProgressUpdate(progress)
            } catch (e) {
              console.warn('Failed to parse progress data:', data)
            }
          }
        }
      }
    } catch (error) {
      console.error('Processing error:', error)
      updateStep(currentStep || 'upload', 'error', { error: error.message })
      setIsProcessing(false)
    }
  }

  const handleProgressUpdate = (progress) => {
    const { stage, documentType: detectedType, result, workflowData, error } = progress

    if (error) {
      updateStep(currentStep || 'upload', 'error', { error })
      return
    }

    // Update document type when detected
    if (detectedType) {
      setDocumentType(detectedType)
    }

    // Map API stages to UI steps
    const stageMap = {
      'initializing': 'upload',
      'pdf_analysis': 'pdf_analysis',
      'classification': 'ai_classification',
      'vision_extraction': 'vision_extraction',
      'structure_parsing': 'structure_parsing',
      'crm_integration': 'crm_integration',
      'workflow_automation': 'workflow_automation',
      'complete': 'complete'
    }

    const stepId = stageMap[stage] || stage
    
    if (stepId) {
      const status = stage === 'complete' ? 'completed' : 'active'
      updateStep(stepId, status, {
        message: progress.message,
        ...progress
      })
    }

    // Handle completion
    if (stage === 'complete' && result) {
      onProcessingComplete(result)
    }

    // Handle workflow triggers
    if (workflowData) {
      onWorkflowTriggered(workflowData)
    }
  }

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      processDocument(acceptedFiles[0])
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    multiple: false,
    disabled: isProcessing
  })

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Universal Document AI Processor
        </h2>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Drop any document and watch our AI automatically classify, extract, and process it through intelligent workflows.
          Supports invoices, financial statements, medical bills, legal documents, and more.
        </p>
      </div>

      {/* Stats Bar */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{processedCount}</div>
            <div className="text-sm text-gray-600">Documents Processed</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">7</div>
            <div className="text-sm text-gray-600">Document Types</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">5</div>
            <div className="text-sm text-gray-600">AI Workflows</div>
          </div>
          <div className="text-center">
            <button
              onClick={onViewCRM}
              className="text-2xl font-bold text-pink-600 hover:text-pink-700 transition-colors"
            >
              View CRM →
            </button>
            <div className="text-sm text-gray-600">Database Records</div>
          </div>
        </div>
      </div>

      {/* Document Types */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Supported Document Types</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
          {DOCUMENT_TYPES.map((type) => (
            <div
              key={type.type}
              className={`p-4 rounded-lg border-2 text-center transition-all ${
                documentType === type.type
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="text-2xl mb-2">{type.icon}</div>
              <div className="text-sm font-medium text-gray-900">{type.label}</div>
              <div className="text-xs text-gray-500 mt-1">{type.description}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Drag and Drop Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-12 text-center transition-all ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : isProcessing
            ? 'border-gray-300 bg-gray-50 cursor-not-allowed'
            : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50 cursor-pointer'
        }`}
      >
        <input {...getInputProps()} />
        
        {isProcessing ? (
          <div className="space-y-4">
            <div className="text-4xl">⚡</div>
            <div className="text-xl font-semibold text-gray-700">
              Processing {uploadedFile?.name}...
            </div>
            <div className="text-gray-500">
              AI is analyzing your document
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-6xl">📄</div>
            <div className="text-xl font-semibold text-gray-700">
              {isDragActive ? 'Drop your document here' : 'Drag & drop a PDF document'}
            </div>
            <div className="text-gray-500">
              or click to select a file
            </div>
            <div className="text-sm text-gray-400">
              Supports PDF files up to 50MB
            </div>
          </div>
        )}
      </div>

      {/* Processing Pipeline Visualization */}
      {processingSteps.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">
            🤖 AI Processing Pipeline
          </h3>
          
          <div className="space-y-4">
            {processingSteps.map((step, index) => (
              <div key={step.id} className="flex items-center space-x-4">
                {/* Step Icon */}
                <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                  step.status === 'completed'
                    ? 'bg-green-100 text-green-600'
                    : step.status === 'active'
                    ? `bg-${step.color}-100 text-${step.color}-600 animate-pulse`
                    : step.status === 'error'
                    ? 'bg-red-100 text-red-600'
                    : 'bg-gray-100 text-gray-400'
                }`}>
                  {step.status === 'completed' ? '✓' : 
                   step.status === 'error' ? '✗' : 
                   step.icon}
                </div>

                {/* Step Content */}
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-medium text-gray-900">
                      {step.title}
                    </h4>
                    <span className="text-xs text-gray-500">
                      {step.timestamp?.toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    {step.message || step.description}
                  </p>
                  
                  {/* Additional details */}
                  {step.fileName && (
                    <div className="text-xs text-gray-500 mt-1">
                      📄 {step.fileName} ({step.fileSize})
                    </div>
                  )}
                  {step.currentPage && step.totalPages && (
                    <div className="text-xs text-gray-500 mt-1">
                      📄 Page {step.currentPage} of {step.totalPages}
                    </div>
                  )}
                  {step.totalCost && (
                    <div className="text-xs text-gray-500 mt-1">
                      💰 Processing cost: ${step.totalCost.toFixed(4)}
                    </div>
                  )}
                  {step.error && (
                    <div className="text-xs text-red-600 mt-1">
                      ❌ Error: {step.error}
                    </div>
                  )}
                </div>

                {/* Progress Line */}
                {index < processingSteps.length - 1 && (
                  <div className="absolute left-5 mt-12 w-0.5 h-8 bg-gray-200"></div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default UniversalProcessor