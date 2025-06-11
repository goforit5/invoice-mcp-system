import React, { useState, useEffect } from 'react'
import axios from 'axios'

const InvoiceDatabase = ({ onBack, onViewRecord }) => {
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

  const getStatusColor = (status) => {
    switch (status?.toUpperCase()) {
      case 'COMPLETE':
        return 'bg-invoice-green/10 text-invoice-green border-invoice-green/20'
      case 'PARTIAL':
        return 'bg-invoice-orange/10 text-invoice-orange border-invoice-orange/20'
      default:
        return 'bg-gray-100 text-gray-500 border-gray-200'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-2 border-invoice-blue border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
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
            className="flex items-center space-x-2 text-invoice-blue font-semibold hover:text-invoice-blue/80 transition-colors"
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
          Invoice Database
        </h1>
        <p className="text-gray-600 text-lg font-light">
          View all processed invoices and extraction results
        </p>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="px-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="bg-invoice-blue/10 border border-invoice-blue/20 rounded-2xl p-6">
              <div className="text-2xl font-bold text-invoice-blue mb-1">
                {stats.totalProcessed}
              </div>
              <div className="text-sm font-medium text-gray-600">
                Total Processed
              </div>
            </div>
            
            <div className="bg-invoice-green/10 border border-invoice-green/20 rounded-2xl p-6">
              <div className="text-2xl font-bold text-invoice-green mb-1">
                ${stats.totalCost.toFixed(4)}
              </div>
              <div className="text-sm font-medium text-gray-600">
                Processing Cost
              </div>
            </div>
            
            <div className="bg-invoice-orange/10 border border-invoice-orange/20 rounded-2xl p-6">
              <div className="text-2xl font-bold text-invoice-orange mb-1">
                {formatCurrency(stats.totalInvoiceValue)}
              </div>
              <div className="text-sm font-medium text-gray-600">
                Total Invoice Value
              </div>
            </div>
            
            <div className="bg-green-100 border border-green-200 rounded-2xl p-6">
              <div className="text-2xl font-bold text-green-600 mb-1">
                {stats.autoProcessed}
              </div>
              <div className="text-sm font-medium text-gray-600">
                Auto Processed
              </div>
            </div>
            
            <div className="bg-red-100 border border-red-200 rounded-2xl p-6">
              <div className="text-2xl font-bold text-red-600 mb-1">
                {stats.humanReviewRequired}
              </div>
              <div className="text-sm font-medium text-gray-600">
                Need Review
              </div>
            </div>
          </div>
          
          <div className="mt-4 text-center">
            <div className="inline-flex items-center space-x-2 bg-gray-100 rounded-xl px-4 py-2">
              <div className="w-2 h-2 bg-invoice-green rounded-full"></div>
              <span className="text-sm font-medium text-gray-700">
                {stats.automationRate}% automation rate
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Records Table */}
      <div className="px-6 pb-12">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-xl p-4">
            <div className="flex items-center space-x-3">
              <div className="w-5 h-5 text-red-500">
                <svg fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h4 className="font-semibold text-red-800">Database Error</h4>
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            </div>
          </div>
        )}

        {records.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-black mb-2">No invoices processed yet</h3>
            <p className="text-gray-500">Upload your first invoice to see processing results here</p>
          </div>
        ) : (
          <div className="bg-gray-50 rounded-2xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-100">
                  <tr>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Invoice</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Vendor</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Customer</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Amount</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Status</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Processed</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Cost</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {records.map((record, index) => (
                    <tr key={record.id || index} className="hover:bg-gray-50/50 transition-colors">
                      <td className="px-6 py-4">
                        <div>
                          <div className="font-semibold text-black text-sm">
                            {record.invoice_number || 'No number'}
                          </div>
                          <div className="text-xs text-gray-500 truncate max-w-[200px]">
                            {record.original_filename}
                          </div>
                        </div>
                      </td>
                      
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-black max-w-[150px] truncate">
                          {record.vendor_name || 'Unknown'}
                        </div>
                      </td>
                      
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-black max-w-[150px] truncate">
                          {record.customer_name || 'Unknown'}
                        </div>
                      </td>
                      
                      <td className="px-6 py-4">
                        <div className="text-sm font-semibold text-black">
                          {formatCurrency(record.total_amount)}
                        </div>
                      </td>
                      
                      <td className="px-6 py-4">
                        <div className={`inline-flex px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(record.status)}`}>
                          {record.status || 'UNKNOWN'}
                        </div>
                      </td>
                      
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-600">
                          {formatDate(record.timestamp)}
                        </div>
                      </td>
                      
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-black">
                          ${parseFloat(record.total_cost || 0).toFixed(4)}
                        </div>
                      </td>
                      
                      <td className="px-6 py-4">
                        <button
                          onClick={() => handleViewRecord(record.id)}
                          className="bg-invoice-blue text-white text-sm font-semibold py-1 px-3 rounded-lg hover:bg-invoice-blue/90 transition-colors"
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            {/* Pagination Info */}
            <div className="bg-gray-100 px-6 py-3 border-t border-gray-200">
              <div className="flex items-center justify-between text-sm text-gray-600">
                <div>
                  Showing {records.length} records
                </div>
                <div>
                  Total processing cost: ${stats?.totalCost.toFixed(4) || '0.0000'}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Invoice Types Legend */}
      <div className="px-6 pb-12">
        <div className="bg-gray-50 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-black mb-4">Invoice Processing Guide</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="flex items-start space-x-3">
              <div className="w-3 h-3 bg-invoice-green rounded-full mt-1"></div>
              <div>
                <div className="font-semibold text-black">Complete Status</div>
                <div className="text-gray-600">All required fields extracted successfully</div>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-3 h-3 bg-invoice-orange rounded-full mt-1"></div>
              <div>
                <div className="font-semibold text-black">Partial Status</div>
                <div className="text-gray-600">Some fields missing, may need review</div>
              </div>
            </div>
            
            <div className="flex items-start space-x-3">
              <div className="w-3 h-3 bg-invoice-blue rounded-full mt-1"></div>
              <div>
                <div className="font-semibold text-black">Processing Cost</div>
                <div className="text-gray-600">Based on AI vision + LLM usage</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default InvoiceDatabase