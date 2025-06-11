import React, { useState, useEffect } from 'react'
import axios from 'axios'

const DatabaseView = ({ onBack, onViewRecord }) => {
  const [records, setRecords] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [databaseResponse, statsResponse] = await Promise.all([
        axios.get('/api/database'),
        axios.get('/api/stats')
      ])
      
      setRecords(databaseResponse.data.records || [])
      setStats(statsResponse.data)
      setError(null)
    } catch (error) {
      console.error('Error loading database:', error)
      setError('Failed to load database records')
    } finally {
      setLoading(false)
    }
  }

  const handleViewRecord = async (recordId) => {
    try {
      const response = await axios.get(`/api/record/${recordId}`)
      onViewRecord(response.data)
    } catch (error) {
      console.error('Error loading record:', error)
      setError('Failed to load record details')
    }
  }

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatCurrency = (value) => {
    if (!value) return 'N/A'
    return `$${parseFloat(value).toLocaleString()}`
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-electric-cyan border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading database...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="px-6 pt-16 pb-8">
        <div className="flex items-center justify-between mb-6">
          <button 
            onClick={onBack}
            className="flex items-center space-x-2 text-electric-cyan font-semibold hover:text-electric-cyan/80 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span>Back</span>
          </button>
          
          <button 
            onClick={loadData}
            className="bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold py-2 px-4 rounded-xl transition-colors"
          >
            Refresh
          </button>
        </div>

        <h1 className="text-4xl font-bold text-black tracking-tight mb-2">
          Processing Database
        </h1>
        <p className="text-gray-600 text-lg font-light">
          View all processed brokerage statements and audit results
        </p>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="px-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-electric-cyan/5 border border-electric-cyan/20 rounded-2xl p-6 text-center">
              <div className="text-3xl font-bold text-black mb-1">{stats.totalProcessed}</div>
              <div className="text-gray-600 text-sm font-medium">Total Processed</div>
            </div>
            
            <div className="bg-green-50 border border-green-200 rounded-2xl p-6 text-center">
              <div className="text-3xl font-bold text-green-600 mb-1">{stats.automationRate}%</div>
              <div className="text-gray-600 text-sm font-medium">Automation Rate</div>
            </div>
            
            <div className="bg-gray-50 rounded-2xl p-6 text-center">
              <div className="text-3xl font-bold text-black mb-1">${stats.totalCost}</div>
              <div className="text-gray-600 text-sm font-medium">Total Cost</div>
            </div>
            
            <div className="bg-orange-50 border border-orange-200 rounded-2xl p-6 text-center">
              <div className="text-3xl font-bold text-orange-600 mb-1">{stats.humanReviewRequired}</div>
              <div className="text-gray-600 text-sm font-medium">Manual Reviews</div>
            </div>
          </div>
        </div>
      )}

      {/* Records List */}
      <div className="px-6 pb-12">
        {error && (
          <div className="mb-6 bg-gentle-rose border border-red-200 rounded-xl p-4">
            <div className="flex items-center space-x-3">
              <div className="w-5 h-5 text-red-500">
                <svg fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h4 className="font-semibold text-red-800">Error</h4>
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            </div>
          </div>
        )}

        {records.length === 0 ? (
          <div className="bg-gray-50 rounded-2xl p-12 text-center">
            <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-black mb-2">No records found</h3>
            <p className="text-gray-600">Upload and process some documents to see them here.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {records.map((record, index) => (
              <div 
                key={record.id || index}
                className="bg-gray-50 rounded-2xl p-6 hover:bg-gray-100 transition-colors cursor-pointer"
                onClick={() => handleViewRecord(record.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-4 mb-3">
                      <h3 className="font-semibold text-black text-lg">{record.original_filename}</h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        record.overall_status === 'pass' 
                          ? 'bg-green-100 text-green-600' 
                          : 'bg-orange-100 text-orange-600'
                      }`}>
                        {record.overall_status?.toUpperCase() || 'UNKNOWN'}
                      </span>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        record.requires_human_review === 'false' 
                          ? 'bg-electric-cyan/10 text-electric-cyan' 
                          : 'bg-orange-100 text-orange-600'
                      }`}>
                        {record.requires_human_review === 'false' ? 'AUTO PROCESSED' : 'MANUAL REVIEW'}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-6 gap-4 text-sm">
                      <div>
                        <div className="text-gray-600 font-medium">Pages</div>
                        <div className="text-black">{record.pages_processed || '1'}</div>
                      </div>
                      <div>
                        <div className="text-gray-600 font-medium">Accounts</div>
                        <div className="text-black">{record.accounts_found || '0'}</div>
                      </div>
                      <div>
                        <div className="text-gray-600 font-medium">Holdings</div>
                        <div className="text-black">{record.holdings_count || '0'}</div>
                      </div>
                      <div>
                        <div className="text-gray-600 font-medium">Total Value</div>
                        <div className="text-black font-mono">{formatCurrency(record.total_value)}</div>
                      </div>
                      <div>
                        <div className="text-gray-600 font-medium">Processing Cost</div>
                        <div className="text-black font-mono">${parseFloat(record.total_cost || 0).toFixed(4)}</div>
                        <div className="text-gray-500 text-xs">
                          Vision: ${parseFloat(record.vision_cost || 0).toFixed(4)} • LLM: ${parseFloat(record.llm_cost || 0).toFixed(4)}
                        </div>
                      </div>
                      <div>
                        <div className="text-gray-600 font-medium">Automation</div>
                        <div className="text-black font-semibold">{record.automation_rate || '100%'}</div>
                        <div className="text-gray-500 text-xs">{record.processing_time}</div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="ml-6">
                    <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default DatabaseView