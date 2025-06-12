import React, { useState, useCallback, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'

const MCPProcessor = ({ onProcessingComplete }) => {
  const [isProcessing, setIsProcessing] = useState(false)
  const [mcpTools, setMcpTools] = useState([])
  const [mcpStatus, setMcpStatus] = useState(null)
  const [toolCalls, setToolCalls] = useState([])
  const [currentStep, setCurrentStep] = useState(null)
  const [uploadedFile, setUploadedFile] = useState(null)

  useEffect(() => {
    loadMCPStatus()
  }, [])

  const loadMCPStatus = async () => {
    try {
      // Load MCP tools and status
      const [toolsRes, statusRes] = await Promise.all([
        fetch('/api/mcp-tools'),
        fetch('/api/mcp-status')
      ])
      
      const tools = await toolsRes.json()
      const status = await statusRes.json()
      
      setMcpTools(tools.tools)
      setMcpStatus(status)
    } catch (error) {
      console.error('Failed to load MCP info:', error)
    }
  }

  const processDocument = async (file) => {
    setIsProcessing(true)
    setToolCalls([])
    setUploadedFile(file)
    
    try {
      const formData = new FormData()
      formData.append('pdf', file)

      // Start agentic processing
      const response = await fetch('/api/agentic-process', {
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
              setIsProcessing(false)
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
      setIsProcessing(false)
    }
  }

  const handleProgressUpdate = (progress) => {
    const { stage, tool, result, error } = progress

    if (error) {
      setCurrentStep({ stage: 'error', message: error })
      return
    }

    setCurrentStep({
      stage,
      message: progress.message,
      tool: progress.mcpTool
    })

    // Track MCP tool calls
    if (stage === 'mcp_tool_call' && tool) {
      setToolCalls(prev => [...prev, {
        tool,
        timestamp: new Date(),
        status: 'executing'
      }])
    }

    // Handle completion
    if (stage === 'complete' && result) {
      // Update tool calls with results
      if (result.mcp_tools_called) {
        setToolCalls(result.mcp_tools_called.map(call => ({
          ...call,
          timestamp: new Date()
        })))
      }
      onProcessingComplete(result)
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
          🤖 Agentic MCP Document Processor
        </h2>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          100% MCP-based processing. Drop a document and watch as AI agents call MCP tools
          to extract data, create CRM records, and automate workflows.
        </p>
      </div>

      {/* MCP Status */}
      {mcpStatus && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🔌 MCP Server Status</h3>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {mcpStatus.servers.map((server) => (
              <div key={server.name} className="text-center p-3 bg-green-50 rounded-lg">
                <div className="text-sm font-medium text-gray-900">{server.name}</div>
                <div className="text-xs text-gray-600">{server.tools} tools</div>
                <div className="mt-1">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    {server.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
          <div className="mt-4 text-center text-sm text-gray-600">
            Total MCP Tools Available: <span className="font-semibold">{mcpStatus.total_tools}</span>
          </div>
        </div>
      )}

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
            <div className="text-4xl animate-pulse">🤖</div>
            <div className="text-xl font-semibold text-gray-700">
              AI Agent Processing...
            </div>
            {currentStep && (
              <div className="text-sm text-gray-600">
                {currentStep.message}
                {currentStep.tool && (
                  <div className="text-xs text-blue-600 mt-1">
                    Tool: {currentStep.tool}
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-6xl">📄</div>
            <div className="text-xl font-semibold text-gray-700">
              {isDragActive ? 'Drop your document here' : 'Drag & drop a PDF document'}
            </div>
            <div className="text-gray-500">
              AI agents will process it using MCP tools
            </div>
          </div>
        )}
      </div>

      {/* MCP Tool Calls Visualization */}
      {toolCalls.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">
            🔧 MCP Tool Execution Log
          </h3>
          
          <div className="space-y-3">
            {toolCalls.map((call, index) => (
              <div key={index} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                <div className="flex-shrink-0">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    call.status === 'success' 
                      ? 'bg-green-100 text-green-600' 
                      : 'bg-blue-100 text-blue-600 animate-pulse'
                  }`}>
                    {call.status === 'success' ? '✓' : '⚡'}
                  </div>
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-medium text-gray-900">
                      {call.tool}
                    </h4>
                    <span className="text-xs text-gray-500">
                      {call.duration || 'executing...'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    {call.result || 'Processing...'}
                  </p>
                  {call.timestamp && (
                    <p className="text-xs text-gray-400 mt-1">
                      {call.timestamp.toLocaleTimeString()}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Available MCP Tools */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📚 Available MCP Tools</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {mcpTools.map((category, idx) => (
            <div key={idx} className="space-y-3">
              <h4 className="font-medium text-gray-900">{category.category}</h4>
              <div className="space-y-2">
                {category.tools.map((tool, toolIdx) => (
                  <div key={toolIdx} className="text-sm">
                    <div className="font-mono text-xs text-blue-600">{tool.name}</div>
                    <div className="text-gray-600 text-xs">{tool.description}</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default MCPProcessor