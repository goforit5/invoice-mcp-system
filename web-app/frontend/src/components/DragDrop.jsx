import React, { useState, useRef } from 'react'
import axios from 'axios'

const DragDrop = ({ onProcessingComplete, onViewDatabase }) => {
  const [isDragging, setIsDragging] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [processingStage, setProcessingStage] = useState('')
  const [currentPage, setCurrentPage] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [processingDetails, setProcessingDetails] = useState({})
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  const handleDragOver = (e) => {
    e.preventDefault()
    if (!isProcessing) {
      setIsDragging(true)
    }
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    
    if (isProcessing) return

    const files = e.dataTransfer.files
    if (files.length > 0) {
      const file = files[0]
      if (file.type === 'application/pdf') {
        processFile(file)
      } else {
        setError('Please upload a PDF file')
      }
    }
  }

  const handleFileSelect = (e) => {
    if (isProcessing) return
    
    const file = e.target.files[0]
    if (file && file.type === 'application/pdf') {
      processFile(file)
    } else {
      setError('Please select a PDF file')
    }
  }

  const processFile = async (file) => {
    setIsProcessing(true)
    setError(null)
    setCurrentPage(0)
    setTotalPages(0)
    setProcessingDetails({ fileName: file.name, fileSize: `${(file.size / 1024 / 1024).toFixed(1)} MB` })
    
    const formData = new FormData()
    formData.append('pdf', file)

    try {
      // Use Server-Sent Events for real-time progress
      console.log('🚀 Starting upload with SSE...')
      setProcessingStage('Uploading document...')
      
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      })

      console.log('📡 Response received:', response.status, response.headers.get('content-type'))

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let result = null

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim()
            if (data === '[DONE]') {
              break
            }

            try {
              const progressData = JSON.parse(data)
              console.log('📊 Progress update:', progressData.stage, progressData)

              // Update UI based on progress stage
              switch (progressData.stage) {
                case 'initializing':
                  setProcessingStage('Initializing upload...')
                  break
                  
                case 'pdf_analysis':
                  setProcessingStage('Converting PDF to high-resolution images...')
                  break
                  
                case 'vision_extraction':
                  setProcessingStage(progressData.message || 'Processing pages with AI vision...')
                  if (progressData.totalPages) {
                    setTotalPages(progressData.totalPages)
                    setCurrentPage(progressData.currentPage || progressData.totalPages)
                  }
                  break
                  
                case 'structure_parsing':
                  setProcessingStage('Converting to structured data with AI...')
                  if (progressData.totalPages) {
                    setCurrentPage(progressData.totalPages)
                  }
                  break
                  
                case 'saving':
                  setProcessingStage('Validating and saving results...')
                  break
                  
                case 'complete':
                  result = progressData.result
                  setProcessingStage('Processing complete!')
                  
                  // Update final details
                  if (result) {
                    setProcessingDetails({
                      ...processingDetails,
                      totalPages: result.total_pages,
                      processingTime: result.processing_time,
                      costBreakdown: result.cost_breakdown
                    })
                    
                    setTimeout(() => {
                      onProcessingComplete(result)
                    }, 1000)
                  }
                  break
                  
                case 'error':
                  throw new Error(progressData.error)
                  
                default:
                  console.log('⚠️ Unknown progress stage:', progressData.stage, progressData)
                  // Try to extract useful info anyway
                  if (progressData.message) {
                    setProcessingStage(progressData.message)
                  }
              }
            } catch (parseError) {
              console.error('Failed to parse progress data:', parseError, 'Raw data:', data)
            }
          }
        }
      }

      // If we get here without a result, something went wrong
      if (!result) {
        console.warn('⚠️ Processing completed but no result received')
        setProcessingStage('Processing completed - waiting for results...')
        // Try to wait a bit longer
        setTimeout(() => {
          if (!result) {
            setError('Processing completed but results not received')
            setIsProcessing(false)
          }
        }, 5000)
      }

    } catch (error) {
      console.error('Error processing file:', error)
      setError(error.message || 'Failed to process file')
      setIsProcessing(false)
      setProcessingStage('')
      setCurrentPage(0)
      setTotalPages(0)
    }
  }

  const openFileSelector = () => {
    if (!isProcessing) {
      fileInputRef.current?.click()
    }
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="px-6 pt-16 pb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-4xl font-bold text-black tracking-tight mb-2">
              Brokerage Processor
            </h1>
            <p className="text-gray-600 text-lg font-light">
              Upload your brokerage statement for AI-powered extraction
            </p>
          </div>
          <button 
            onClick={onViewDatabase}
            className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-2 px-4 rounded-xl transition-colors"
          >
            View Database
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="px-6">
        {!isProcessing ? (
          /* Upload Area */
          <div
            className={`
              relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-200
              ${isDragging 
                ? 'border-electric-cyan bg-electric-cyan/5 scale-98' 
                : 'border-gray-300 hover:border-electric-cyan hover:bg-gray-50'
              }
              ${!isProcessing ? 'cursor-pointer' : 'cursor-not-allowed opacity-50'}
            `}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={openFileSelector}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
              className="hidden"
            />
            
            {/* Upload Icon */}
            <div className="mb-6">
              <div className={`
                w-20 h-20 mx-auto rounded-full flex items-center justify-center transition-all duration-200
                ${isDragging ? 'bg-electric-cyan text-white' : 'bg-gray-100 text-gray-400'}
              `}>
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
            </div>

            {/* Upload Text */}
            <h3 className="text-xl font-semibold text-black mb-2">
              {isDragging ? 'Drop your PDF here' : 'Drop PDF here or click to upload'}
            </h3>
            <p className="text-gray-500 mb-6">
              Supports brokerage statements from major providers
            </p>

            {/* Upload Button */}
            <button className="bg-electric-cyan text-white font-semibold py-3 px-8 rounded-xl transition-all duration-200 transform active:scale-98 shadow-lg shadow-electric-cyan/25">
              Choose File
            </button>
          </div>
        ) : (
          /* Enhanced Processing State */
          <div className="bg-gray-50 rounded-2xl p-8">
            {/* File Info Header */}
            <div className="text-center mb-6">
              <div className="relative mb-4">
                <div className="w-20 h-20 border-4 border-electric-cyan border-t-electric-cyan/30 rounded-full animate-spin mx-auto"></div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-12 h-12 bg-electric-cyan/20 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-electric-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                </div>
              </div>
              <h3 className="text-2xl font-bold text-black mb-2">
                AI Processing in Progress
              </h3>
              <div className="flex items-center justify-center space-x-4 text-sm text-gray-600">
                <span className="flex items-center">
                  📄 {processingDetails.fileName}
                </span>
                <span>•</span>
                <span className="flex items-center">
                  📊 {processingDetails.fileSize}
                </span>
                {totalPages > 0 && (
                  <>
                    <span>•</span>
                    <span className="flex items-center">
                      📖 {totalPages} pages
                    </span>
                  </>
                )}
              </div>
            </div>

            {/* Live Processing Status */}
            <div className="bg-white rounded-xl p-6 mb-6 border border-electric-cyan/20">
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-semibold text-black">Current Operation</h4>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-electric-cyan rounded-full animate-pulse"></div>
                  <span className="text-sm text-electric-cyan font-medium">ACTIVE</span>
                </div>
              </div>
              
              <div className="text-lg font-medium text-gray-800 mb-3">
                {processingStage}
              </div>
              
              {/* Page Progress Bar with Details */}
              {totalPages > 0 && (
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-700">
                      Processing Progress
                    </span>
                    <span className="text-sm font-mono text-gray-600">
                      {currentPage}/{totalPages} pages ({Math.round((currentPage / totalPages) * 100)}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div 
                      className="bg-gradient-to-r from-electric-cyan to-blue-500 h-3 rounded-full transition-all duration-1000 ease-out relative"
                      style={{ width: `${(currentPage / totalPages) * 100}%` }}
                    >
                      <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-xs text-gray-600">
                    <div className="text-center">
                      <div className="font-medium">Est. Time</div>
                      <div>{Math.ceil((totalPages * 2 + 15) / 60)}min {((totalPages * 2 + 15) % 60)}s</div>
                    </div>
                    <div className="text-center">
                      <div className="font-medium">Processing Rate</div>
                      <div>~2s per page</div>
                    </div>
                    <div className="text-center">
                      <div className="font-medium">Est. Cost</div>
                      <div>${((totalPages * 0.002) + 0.015).toFixed(3)}</div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Detailed Processing Pipeline */}
            <div className="space-y-4">
              <h4 className="font-semibold text-black mb-4">AI Processing Pipeline</h4>
              
              {/* Stage 1: PDF Analysis */}
              <div className={`bg-white rounded-xl p-4 border-l-4 transition-all duration-500 ${
                processingStage.includes('Converting PDF to high-resolution') || processingStage.includes('Initializing')
                  ? 'border-electric-cyan shadow-lg shadow-electric-cyan/10' 
                  : (processingStage.includes('Starting AI') || processingStage.includes('Processing pages') || currentPage > 0)
                    ? 'border-green-400' 
                    : 'border-gray-200'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold ${
                      processingStage.includes('Converting PDF to high-resolution') || processingStage.includes('Initializing')
                        ? 'bg-electric-cyan animate-pulse' 
                        : (processingStage.includes('Starting AI') || processingStage.includes('Processing pages') || currentPage > 0)
                          ? 'bg-green-500' 
                          : 'bg-gray-300'
                    }`}>
                      {(processingStage.includes('Starting AI') || processingStage.includes('Processing pages') || currentPage > 0) ? '✓' : '1'}
                    </div>
                    <div>
                      <div className="font-semibold text-black">PDF Document Analysis</div>
                      <div className="text-sm text-gray-600">
                        {processingStage.includes('Converting PDF to high-resolution') || processingStage.includes('Initializing')
                          ? 'Converting PDF pages to high-resolution images for AI vision processing...'
                          : (processingStage.includes('Starting AI') || processingStage.includes('Processing pages') || currentPage > 0)
                            ? 'Document successfully converted to processable format'
                            : 'Waiting to start document conversion'
                        }
                      </div>
                    </div>
                  </div>
                  {(processingStage.includes('Converting PDF to high-resolution') || processingStage.includes('Initializing')) && (
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 border-2 border-electric-cyan border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-xs text-electric-cyan font-medium">PROCESSING</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Stage 2: AI Vision Extraction */}
              <div className={`bg-white rounded-xl p-4 border-l-4 transition-all duration-500 ${
                processingStage.includes('Starting AI') || processingStage.includes('Processing pages') || processingStage.includes('AI vision')
                  ? 'border-electric-cyan shadow-lg shadow-electric-cyan/10' 
                  : processingStage.includes('Converting to structured') || processingStage.includes('complete')
                    ? 'border-green-400' 
                    : 'border-gray-200'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold ${
                      processingStage.includes('Starting AI') || processingStage.includes('Processing pages') || processingStage.includes('AI vision')
                        ? 'bg-electric-cyan animate-pulse' 
                        : processingStage.includes('Converting to structured') || processingStage.includes('complete')
                          ? 'bg-green-500' 
                          : 'bg-gray-300'
                    }`}>
                      {processingStage.includes('Converting to structured') || processingStage.includes('complete') ? '✓' : '2'}
                    </div>
                    <div className="flex-1">
                      <div className="font-semibold text-black">AI Vision Text Extraction</div>
                      <div className="text-sm text-gray-600">
                        {processingStage.includes('Starting AI')
                          ? 'Initializing OpenAI Vision AI for financial document processing...'
                          : processingStage.includes('Processing pages') || processingStage.includes('AI vision')
                            ? `OpenAI Vision AI reading financial data from each page...`
                            : processingStage.includes('Converting to structured') || processingStage.includes('complete')
                              ? `Successfully extracted text from ${totalPages || 'all'} pages`
                              : 'Waiting for document conversion to complete'
                        }
                      </div>
                      {currentPage > 0 && totalPages > 0 && (
                        <div className="mt-2">
                          <div className="flex items-center space-x-2 text-xs">
                            <span className="text-gray-500">Progress:</span>
                            <span className="font-mono text-electric-cyan">{currentPage}/{totalPages} pages</span>
                            <span className="text-gray-400">•</span>
                            <span className="text-gray-500">~{(currentPage * 2).toFixed(0)}s elapsed</span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                  {(processingStage.includes('Starting AI') || processingStage.includes('Processing pages') || processingStage.includes('AI vision')) && (
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 border-2 border-electric-cyan border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-xs text-electric-cyan font-medium">AI READING</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Stage 3: Structured Data Processing */}
              <div className={`bg-white rounded-xl p-4 border-l-4 transition-all duration-500 ${
                processingStage.includes('Converting to structured') || processingStage.includes('Validating')
                  ? 'border-electric-cyan shadow-lg shadow-electric-cyan/10' 
                  : processingStage.includes('complete')
                    ? 'border-green-400' 
                    : 'border-gray-200'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold ${
                      processingStage.includes('Converting to structured') || processingStage.includes('Validating')
                        ? 'bg-electric-cyan animate-pulse' 
                        : processingStage.includes('complete')
                          ? 'bg-green-500' 
                          : 'bg-gray-300'
                    }`}>
                      {processingStage.includes('complete') ? '✓' : '3'}
                    </div>
                    <div>
                      <div className="font-semibold text-black">Structured Data Processing</div>
                      <div className="text-sm text-gray-600">
                        {processingStage.includes('Converting to structured')
                          ? 'AI parsing text into structured financial data format...'
                          : processingStage.includes('Validating')
                            ? 'Running validation checks and audit procedures...'
                            : processingStage.includes('complete')
                              ? 'Document processing completed successfully'
                              : 'Waiting for text extraction to complete'
                        }
                      </div>
                    </div>
                  </div>
                  {(processingStage.includes('Converting to structured') || processingStage.includes('Validating')) && (
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 border-2 border-electric-cyan border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-xs text-electric-cyan font-medium">STRUCTURING</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Technical Details */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <details className="group">
                <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-black flex items-center">
                  <svg className="w-4 h-4 mr-2 transform group-open:rotate-90 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  Technical Processing Details
                </summary>
                <div className="mt-3 pl-6 text-xs text-gray-600 space-y-2">
                  <div>🤖 <strong>AI Models:</strong> OpenAI GPT-4.1-mini for vision and structured parsing</div>
                  <div>📸 <strong>Image Processing:</strong> 200 DPI PNG conversion for optimal text recognition</div>
                  <div>🔍 <strong>Vision Processing:</strong> ~2 seconds per page with detailed financial data extraction</div>
                  <div>📊 <strong>Structure Parsing:</strong> 109-field brokerage template with comprehensive audit validation</div>
                  <div>✅ <strong>Validation:</strong> 12 automated audit checks including balance reconciliation</div>
                  <div>💰 <strong>Cost Optimization:</strong> Efficient token usage with specialized financial prompts</div>
                </div>
              </details>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="mt-6 bg-gentle-rose border border-red-200 rounded-xl p-4">
            <div className="flex items-center space-x-3">
              <div className="w-5 h-5 text-red-500">
                <svg fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h4 className="font-semibold text-red-800">Upload Error</h4>
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Help Text */}
        <div className="mt-12 text-center">
          <h4 className="font-semibold text-black mb-4">Supported Documents</h4>
          <div className="flex justify-center space-x-8 text-sm text-gray-600">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>Fidelity Statements</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>Charles Schwab</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>E*TRADE</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DragDrop