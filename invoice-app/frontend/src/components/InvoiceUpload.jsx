import React, { useState, useRef } from 'react'
import axios from 'axios'

const InvoiceUpload = ({ onProcessingComplete, onViewDatabase }) => {
  const [isDragging, setIsDragging] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [processingStage, setProcessingStage] = useState('')
  const [currentPage, setCurrentPage] = useState(0)
  const [totalPages, setTotalPages] = useState(0)
  const [processingDetails, setProcessingDetails] = useState({})
  const [error, setError] = useState(null)
  const [progressMessage, setProgressMessage] = useState('')
  const fileInputRef = useRef(null)
  const eventSourceRef = useRef(null)

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
    setProcessingStage('Uploading...')
    setProgressMessage('Preparing file for processing...')
    setProcessingDetails({ fileName: file.name, fileSize: `${(file.size / 1024 / 1024).toFixed(1)} MB` })
    
    // Connect to progress updates
    eventSourceRef.current = new EventSource('/api/progress')
    
    eventSourceRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        switch (data.stage) {
          case 'connected':
            console.log('Connected to progress updates')
            break
          case 'starting':
            setProcessingStage('Initializing...')
            setProgressMessage(data.message || 'Starting PDF processing...')
            break
          case 'processing':
            setProcessingStage('Processing PDF...')
            setProgressMessage(data.message || 'Converting PDF to images...')
            break
          case 'text_complete':
            setProcessingStage('Analyzing Content...')
            setProgressMessage(data.message || 'Text extraction complete...')
            break
          case 'structuring':
            setProcessingStage('Structuring Data...')
            setProgressMessage(data.message || 'AI parsing invoice data...')
            break
          case 'structured_complete':
            setProcessingStage('Extracting Data...')
            setProgressMessage(data.message || 'Data extraction complete...')
            break
          case 'saving':
            setProcessingStage('Finalizing...')
            setProgressMessage(data.message || 'Saving results...')
            break
          case 'saved':
            setProcessingStage('Complete!')
            setProgressMessage(data.message || 'Processing complete!')
            break
          case 'complete':
            setProcessingStage('Complete!')
            setProgressMessage(data.message || 'Processing complete!')
            eventSourceRef.current?.close()
            break
          case 'error':
            setError(data.message || 'Processing failed')
            setIsProcessing(false)
            setProcessingStage('')
            setProgressMessage('')
            eventSourceRef.current?.close()
            break
        }
      } catch (e) {
        console.error('Error parsing progress data:', e)
      }
    }
    
    eventSourceRef.current.onerror = (error) => {
      console.error('EventSource error:', error)
      eventSourceRef.current?.close()
    }

    const formData = new FormData()
    formData.append('pdf', file)

    try {
      // Use traditional POST request for invoice processing
      const response = await axios.post('/api/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      if (response.data.success) {
        setProcessingDetails({
          ...processingDetails,
          totalPages: response.data.result.total_pages,
          processingTime: response.data.result.processing_time,
          costBreakdown: response.data.result.cost_breakdown
        })
        
        setTimeout(() => {
          setIsProcessing(false)
          onProcessingComplete(response.data.result)
        }, 2000)
      } else {
        throw new Error(response.data.error || 'Processing failed')
      }

    } catch (error) {
      console.error('Error processing file:', error)
      setError(error.response?.data?.details || error.message || 'Failed to process file')
      setIsProcessing(false)
      setProcessingStage('')
      setProgressMessage('')
      setCurrentPage(0)
      setTotalPages(0)
      eventSourceRef.current?.close()
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
              Invoice Processor
            </h1>
            <p className="text-gray-600 text-lg font-light">
              Upload your invoice for AI-powered data extraction
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
                ? 'border-invoice-blue bg-invoice-blue/5 scale-98' 
                : 'border-gray-300 hover:border-invoice-blue hover:bg-gray-50'
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
                ${isDragging ? 'bg-invoice-blue text-white' : 'bg-gray-100 text-gray-400'}
              `}>
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>

            {/* Upload Text */}
            <h3 className="text-xl font-semibold text-black mb-2">
              {isDragging ? 'Drop your invoice here' : 'Drop invoice PDF here or click to upload'}
            </h3>
            <p className="text-gray-500 mb-6">
              Supports invoices from any vendor or service provider
            </p>

            {/* Upload Button */}
            <button className="bg-invoice-blue text-white font-semibold py-3 px-8 rounded-xl transition-all duration-200 transform active:scale-98 shadow-lg shadow-invoice-blue/25">
              Choose File
            </button>
          </div>
        ) : (
          /* Enhanced Processing State */
          <div className="bg-gray-50 rounded-2xl p-8">
            {/* File Info Header */}
            <div className="text-center mb-6">
              <div className="relative mb-4">
                <div className="w-20 h-20 border-4 border-invoice-blue border-t-invoice-blue/30 rounded-full animate-spin mx-auto"></div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-12 h-12 bg-invoice-blue/20 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-invoice-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
            <div className="bg-white rounded-xl p-6 mb-6 border border-invoice-blue/20">
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-semibold text-black">Current Operation</h4>
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-invoice-blue rounded-full animate-pulse"></div>
                  <span className="text-sm text-invoice-blue font-medium">ACTIVE</span>
                </div>
              </div>
              
              <div className="text-lg font-medium text-gray-800 mb-3">
                {processingStage || 'Extracting invoice data...'}
              </div>
              
              {progressMessage && (
                <div className="text-sm text-gray-600 mb-3">
                  {progressMessage}
                </div>
              )}
              
              {/* Progress Bar with Details */}
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
                      className="bg-gradient-to-r from-invoice-blue to-blue-500 h-3 rounded-full transition-all duration-1000 ease-out relative"
                      style={{ width: `${(currentPage / totalPages) * 100}%` }}
                    >
                      <div className="absolute inset-0 bg-white/20 animate-pulse"></div>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-xs text-gray-600">
                    <div className="text-center">
                      <div className="font-medium">Est. Time</div>
                      <div>{Math.ceil((totalPages * 1.5 + 10) / 60)}min {((totalPages * 1.5 + 10) % 60)}s</div>
                    </div>
                    <div className="text-center">
                      <div className="font-medium">Processing Rate</div>
                      <div>~1.5s per page</div>
                    </div>
                    <div className="text-center">
                      <div className="font-medium">Est. Cost</div>
                      <div>${((totalPages * 0.001) + 0.01).toFixed(3)}</div>
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
                processingStage.includes('Uploading') || processingStage.includes('Initializing')
                  ? 'border-invoice-blue shadow-lg shadow-invoice-blue/10' 
                  : processingStage.includes('Processing') || currentPage > 0
                    ? 'border-green-400' 
                    : 'border-gray-200'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold ${
                      processingStage.includes('Uploading') || processingStage.includes('Initializing')
                        ? 'bg-invoice-blue animate-pulse' 
                        : processingStage.includes('Processing') || currentPage > 0
                          ? 'bg-green-500' 
                          : 'bg-gray-300'
                    }`}>
                      {processingStage.includes('Processing') || currentPage > 0 ? '✓' : '1'}
                    </div>
                    <div>
                      <div className="font-semibold text-black">PDF Document Analysis</div>
                      <div className="text-sm text-gray-600">
                        {processingStage.includes('Uploading') || processingStage.includes('Initializing')
                          ? 'Converting PDF pages to high-resolution images for AI vision processing...'
                          : processingStage.includes('Processing') || currentPage > 0
                            ? 'Document successfully converted to processable format'
                            : 'Waiting to start document conversion'
                        }
                      </div>
                    </div>
                  </div>
                  {(processingStage.includes('Uploading') || processingStage.includes('Initializing')) && (
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 border-2 border-invoice-blue border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-xs text-invoice-blue font-medium">PROCESSING</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Stage 2: AI Vision Extraction */}
              <div className={`bg-white rounded-xl p-4 border-l-4 transition-all duration-500 ${
                processingStage.includes('Processing PDF') || processingStage.includes('Analyzing')
                  ? 'border-invoice-blue shadow-lg shadow-invoice-blue/10' 
                  : processingStage.includes('Extracting') || processingStage.includes('Finalizing')
                    ? 'border-green-400' 
                    : 'border-gray-200'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold ${
                      processingStage.includes('Processing PDF') || processingStage.includes('Analyzing')
                        ? 'bg-invoice-blue animate-pulse' 
                        : processingStage.includes('Extracting') || processingStage.includes('Finalizing')
                          ? 'bg-green-500' 
                          : 'bg-gray-300'
                    }`}>
                      {processingStage.includes('Extracting') || processingStage.includes('Finalizing') ? '✓' : '2'}
                    </div>
                    <div className="flex-1">
                      <div className="font-semibold text-black">AI Vision Text Extraction</div>
                      <div className="text-sm text-gray-600">
                        {processingStage.includes('Processing PDF') || processingStage.includes('Analyzing')
                          ? 'OpenAI Vision AI reading invoice data from each page...'
                          : processingStage.includes('Extracting') || processingStage.includes('Finalizing')
                            ? `Successfully extracted text from ${totalPages || 'all'} pages`
                            : 'Waiting for document conversion to complete'
                        }
                      </div>
                    </div>
                  </div>
                  {(processingStage.includes('Processing PDF') || processingStage.includes('Analyzing')) && (
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 border-2 border-invoice-blue border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-xs text-invoice-blue font-medium">AI READING</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Stage 3: Structured Data Processing */}
              <div className={`bg-white rounded-xl p-4 border-l-4 transition-all duration-500 ${
                processingStage.includes('Extracting Data') || processingStage.includes('Finalizing')
                  ? 'border-invoice-blue shadow-lg shadow-invoice-blue/10' 
                  : processingStage.includes('Complete')
                    ? 'border-green-400' 
                    : 'border-gray-200'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold ${
                      processingStage.includes('Extracting Data') || processingStage.includes('Finalizing')
                        ? 'bg-invoice-blue animate-pulse' 
                        : processingStage.includes('Complete')
                          ? 'bg-green-500' 
                          : 'bg-gray-300'
                    }`}>
                      {processingStage.includes('Complete') ? '✓' : '3'}
                    </div>
                    <div>
                      <div className="font-semibold text-black">Structured Data Processing</div>
                      <div className="text-sm text-gray-600">
                        {processingStage.includes('Extracting Data')
                          ? 'AI parsing text into structured invoice data format...'
                          : processingStage.includes('Finalizing')
                            ? 'Running validation checks and saving structured data...'
                            : processingStage.includes('Complete')
                              ? 'Invoice processing completed successfully'
                              : 'Waiting for text extraction to complete'
                        }
                      </div>
                    </div>
                  </div>
                  {(processingStage.includes('Extracting Data') || processingStage.includes('Finalizing')) && (
                    <div className="flex items-center space-x-2">
                      <div className="w-4 h-4 border-2 border-invoice-blue border-t-transparent rounded-full animate-spin"></div>
                      <span className="text-xs text-invoice-blue font-medium">STRUCTURING</span>
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
                  <div>🤖 <strong>AI Models:</strong> OpenAI GPT-4o-mini for vision and structured parsing</div>
                  <div>📸 <strong>Image Processing:</strong> 200 DPI PNG conversion for optimal text recognition</div>
                  <div>🔍 <strong>Vision Processing:</strong> ~1.5 seconds per page with detailed invoice data extraction</div>
                  <div>📊 <strong>Structure Parsing:</strong> Invoice-specific template with vendor, customer, and line item extraction</div>
                  <div>✅ <strong>Validation:</strong> Automated checks for totals, dates, and required fields</div>
                  <div>💰 <strong>Cost Optimization:</strong> Efficient token usage with specialized invoice prompts</div>
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
          <h4 className="font-semibold text-black mb-4">Supported Invoice Types</h4>
          <div className="flex justify-center space-x-8 text-sm text-gray-600">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-invoice-green rounded-full"></div>
              <span>Service Invoices</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-invoice-green rounded-full"></div>
              <span>Product Invoices</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-invoice-green rounded-full"></div>
              <span>Utility Bills</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-invoice-green rounded-full"></div>
              <span>Contractor Invoices</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default InvoiceUpload