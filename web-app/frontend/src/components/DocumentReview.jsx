import React, { useState } from 'react'

const DocumentReview = ({ result, onBack, onViewCRM, onViewWorkflow }) => {
  const [activeTab, setActiveTab] = useState('overview')
  const [showRawData, setShowRawData] = useState(false)

  // Determine document type and get appropriate display data
  const getDocumentTypeInfo = () => {
    const documentType = result.document_type || result.structured_data?.document_metadata?.document_type || 'unknown'
    
    const typeConfig = {
      invoice: { icon: '🧾', label: 'Invoice', color: 'blue' },
      brokerage: { icon: '📊', label: 'Financial Statement', color: 'purple' },
      medical: { icon: '🏥', label: 'Medical Document', color: 'green' },
      dmv: { icon: '🚗', label: 'DMV Document', color: 'red' },
      legal: { icon: '⚖️', label: 'Legal Document', color: 'yellow' },
      tax: { icon: '📋', label: 'Tax Document', color: 'indigo' },
      general: { icon: '📄', label: 'General Document', color: 'gray' }
    }

    return typeConfig[documentType] || typeConfig.general
  }

  const docInfo = getDocumentTypeInfo()
  const structuredData = result.structured_data || {}
  const audit = structuredData.audit || {}

  // Format currency
  const formatCurrency = (amount) => {
    if (!amount && amount !== 0) return 'N/A'
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount)
  }

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    } catch (e) {
      return dateString
    }
  }

  // Get key information based on document type
  const getKeyInformation = () => {
    if (structuredData.invoice_metadata) {
      // Invoice document
      return {
        vendor: structuredData.vendor?.name || 'Unknown Vendor',
        customer: structuredData.customer?.name || 'Unknown Customer',
        amount: formatCurrency(structuredData.totals?.total || structuredData.invoice_metadata?.balance_due),
        date: formatDate(structuredData.invoice_metadata?.issue_date),
        dueDate: formatDate(structuredData.invoice_metadata?.due_date),
        invoiceNumber: structuredData.invoice_metadata?.invoice_number || 'N/A'
      }
    } else if (structuredData.account_summary) {
      // Brokerage document
      return {
        institution: structuredData.account_summary?.institution_name || 'Unknown Institution',
        accountNumber: structuredData.account_summary?.account_number || 'N/A',
        totalValue: formatCurrency(structuredData.statement_total_value),
        statementDate: formatDate(structuredData.statement_date),
        accountsCount: structuredData.accounts?.length || 0,
        holdingsCount: structuredData.accounts?.reduce((total, acc) => total + (acc.holdings?.length || 0), 0) || 0
      }
    } else if (structuredData.document_metadata) {
      // General document
      return {
        title: structuredData.document_metadata?.document_title || result.filename,
        type: structuredData.document_metadata?.document_type || 'General',
        date: formatDate(structuredData.document_metadata?.document_date),
        sender: structuredData.document_metadata?.sender_organization || 'Unknown',
        category: structuredData.document_summary?.category || 'General'
      }
    }
    
    return {}
  }

  const keyInfo = getKeyInformation()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className={`text-4xl p-3 rounded-lg bg-${docInfo.color}-100`}>
            {docInfo.icon}
          </div>
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{docInfo.label} Review</h2>
            <p className="text-gray-600">{result.filename}</p>
            <div className="flex items-center space-x-4 mt-1">
              <span className="text-sm text-gray-500">
                📄 {result.total_pages} page{result.total_pages !== 1 ? 's' : ''}
              </span>
              <span className="text-sm text-gray-500">
                ⏱️ {result.processing_time}
              </span>
              <span className="text-sm text-gray-500">
                💰 ${result.cost_breakdown?.total_cost?.toFixed(4) || '0.0000'}
              </span>
            </div>
          </div>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={onViewWorkflow}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            🤖 View Workflows
          </button>
          <button
            onClick={onViewCRM}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            👥 View in CRM
          </button>
          <button
            onClick={onBack}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            ← Back
          </button>
        </div>
      </div>

      {/* Quick Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(keyInfo).map(([key, value]) => (
          <div key={key} className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <div className="text-sm font-medium text-gray-500 capitalize">
              {key.replace(/([A-Z])/g, ' $1').trim()}
            </div>
            <div className="text-lg font-semibold text-gray-900 mt-1">
              {value || 'N/A'}
            </div>
          </div>
        ))}
      </div>

      {/* Processing Status */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">🔍 Processing Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {audit.overall_status === 'complete' ? '✓' : audit.overall_status === 'requires_human_review' ? '⚠️' : '?'}
            </div>
            <div className="text-sm text-gray-600">Overall Status</div>
            <div className="text-xs text-gray-500 mt-1 capitalize">
              {audit.overall_status?.replace(/_/g, ' ') || 'Unknown'}
            </div>
          </div>
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {result.classification?.confidence ? `${Math.round(result.classification.confidence * 100)}%` : '95%'}
            </div>
            <div className="text-sm text-gray-600">AI Confidence</div>
            <div className="text-xs text-gray-500 mt-1">
              {result.classification?.extractor_used || 'Auto-detected'}
            </div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {audit.requires_human_review ? '👁️' : '🤖'}
            </div>
            <div className="text-sm text-gray-600">Review Status</div>
            <div className="text-xs text-gray-500 mt-1">
              {audit.requires_human_review ? 'Human Review' : 'Fully Automated'}
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'overview', label: '📋 Overview' },
              { id: 'details', label: '🔍 Details' },
              { id: 'extracted_text', label: '📄 Extracted Text' },
              { id: 'audit', label: '✅ Quality Audit' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? `border-${docInfo.color}-500 text-${docInfo.color}-600`
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <div>
                <h4 className="text-lg font-medium text-gray-900 mb-4">Document Summary</h4>
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-gray-700">
                    This {docInfo.label.toLowerCase()} was automatically processed using AI vision and structured data extraction.
                    {audit.overall_status === 'complete' && ' The document was fully processed without issues.'}
                    {audit.requires_human_review && ' Some aspects may require human review for accuracy.'}
                  </p>
                </div>
              </div>

              {/* Line Items for Invoices */}
              {structuredData.line_items && (
                <div>
                  <h4 className="text-lg font-medium text-gray-900 mb-4">Line Items</h4>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Description
                          </th>
                          <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Date
                          </th>
                          <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Amount
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {structuredData.line_items.slice(0, 10).map((item, index) => (
                          <tr key={index}>
                            <td className="px-6 py-4 text-sm text-gray-900">
                              {item.description || 'No description'}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-500">
                              {formatDate(item.date)}
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-900 text-right">
                              {formatCurrency(item.amount)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Holdings for Brokerage */}
              {structuredData.accounts && (
                <div>
                  <h4 className="text-lg font-medium text-gray-900 mb-4">Account Holdings</h4>
                  {structuredData.accounts.slice(0, 3).map((account, accountIndex) => (
                    <div key={accountIndex} className="mb-6">
                      <h5 className="font-medium text-gray-900 mb-2">
                        {account.account_name || `Account ${accountIndex + 1}`}
                      </h5>
                      {account.holdings && (
                        <div className="overflow-x-auto">
                          <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                              <tr>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                  Symbol
                                </th>
                                <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">
                                  Description
                                </th>
                                <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                                  Shares
                                </th>
                                <th className="px-4 py-2 text-right text-xs font-medium text-gray-500 uppercase">
                                  Value
                                </th>
                              </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                              {account.holdings.slice(0, 5).map((holding, index) => (
                                <tr key={index}>
                                  <td className="px-4 py-2 text-sm font-medium text-gray-900">
                                    {holding.symbol || 'N/A'}
                                  </td>
                                  <td className="px-4 py-2 text-sm text-gray-600">
                                    {holding.description || 'No description'}
                                  </td>
                                  <td className="px-4 py-2 text-sm text-gray-900 text-right">
                                    {holding.shares || 'N/A'}
                                  </td>
                                  <td className="px-4 py-2 text-sm text-gray-900 text-right">
                                    {formatCurrency(holding.market_value)}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Details Tab */}
          {activeTab === 'details' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h4 className="text-lg font-medium text-gray-900">Structured Data</h4>
                <button
                  onClick={() => setShowRawData(!showRawData)}
                  className="text-sm text-blue-600 hover:text-blue-700"
                >
                  {showRawData ? 'Hide' : 'Show'} Raw JSON
                </button>
              </div>
              
              {showRawData ? (
                <pre className="bg-gray-100 rounded-lg p-4 text-xs overflow-x-auto">
                  {JSON.stringify(structuredData, null, 2)}
                </pre>
              ) : (
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {Object.entries(keyInfo).map(([key, value]) => (
                      <div key={key}>
                        <span className="text-sm font-medium text-gray-600 capitalize">
                          {key.replace(/([A-Z])/g, ' $1').trim()}:
                        </span>
                        <span className="ml-2 text-sm text-gray-900">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Extracted Text Tab */}
          {activeTab === 'extracted_text' && (
            <div className="space-y-4">
              <h4 className="text-lg font-medium text-gray-900">Extracted Text by Page</h4>
              {result.extracted_text?.map((page, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <h5 className="font-medium text-gray-900 mb-2">
                    Page {page.page || index + 1}
                  </h5>
                  <div className="bg-gray-50 rounded p-3 text-sm text-gray-700 whitespace-pre-wrap max-h-64 overflow-y-auto">
                    {page.text || 'No text extracted from this page'}
                  </div>
                  {page.token_usage && (
                    <div className="mt-2 text-xs text-gray-500">
                      Tokens: {page.token_usage.total_tokens} • Cost: ${page.cost?.total_cost?.toFixed(4) || '0.0000'}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Audit Tab */}
          {activeTab === 'audit' && (
            <div className="space-y-4">
              <h4 className="text-lg font-medium text-gray-900">Quality Audit Report</h4>
              
              {audit.overall_status && (
                <div className={`p-4 rounded-lg ${
                  audit.overall_status === 'complete' ? 'bg-green-50' : 
                  audit.requires_human_review ? 'bg-yellow-50' : 'bg-gray-50'
                }`}>
                  <div className="font-medium">
                    Overall Status: <span className="capitalize">{audit.overall_status.replace(/_/g, ' ')}</span>
                  </div>
                  {audit.requires_human_review && (
                    <div className="text-sm text-yellow-700 mt-1">
                      ⚠️ This document requires human review for optimal accuracy
                    </div>
                  )}
                </div>
              )}

              {audit.missing_sections?.length > 0 && (
                <div className="bg-red-50 p-4 rounded-lg">
                  <div className="font-medium text-red-800">Missing Sections:</div>
                  <ul className="mt-1 text-sm text-red-700">
                    {audit.missing_sections.map((section, index) => (
                      <li key={index}>• {section}</li>
                    ))}
                  </ul>
                </div>
              )}

              {audit.line_math && (
                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="font-medium text-blue-800">Mathematical Validation:</div>
                  <div className="mt-1 text-sm text-blue-700">
                    Line item calculations: {audit.line_math.filter(item => item.status === 'correct').length} / {audit.line_math.length} correct
                  </div>
                </div>
              )}

              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="font-medium text-gray-800">Processing Details:</div>
                <div className="mt-1 text-sm text-gray-600 space-y-1">
                  <div>• Extraction Method: {result.classification?.extractor_used || 'Auto-selected'}</div>
                  <div>• Processing Time: {result.processing_time}</div>
                  <div>• Total Cost: ${result.cost_breakdown?.total_cost?.toFixed(4) || '0.0000'}</div>
                  <div>• Pages Processed: {result.total_pages}</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default DocumentReview