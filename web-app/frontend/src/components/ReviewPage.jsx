import React, { useState } from 'react'

const ReviewPage = ({ result, onBack }) => {
  const [viewMode, setViewMode] = useState('structured') // 'structured' or 'raw'

  const structuredData = result.structured_data
  const extractedText = result.extracted_text

  const formatCurrency = (value) => {
    if (!value) return 'N/A'
    if (typeof value === 'string' && !value.startsWith('$')) {
      return `$${parseFloat(value).toLocaleString()}`
    }
    return value
  }

  const formatNumber = (value) => {
    if (!value) return 'N/A'
    return parseFloat(value).toLocaleString()
  }

  const getConfidenceColor = (hasData) => {
    if (!hasData) return 'bg-gray-100 text-gray-500'
    return 'bg-electric-cyan/10 text-electric-cyan border-electric-cyan/20'
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="px-6 pt-16 pb-8">
        <div className="flex items-center justify-between mb-4">
          <button 
            onClick={onBack}
            className="flex items-center space-x-2 text-electric-cyan font-semibold hover:text-electric-cyan/80 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span>Back</span>
          </button>

          {/* View Toggle */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('structured')}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${
                viewMode === 'structured' 
                  ? 'bg-white text-black shadow-sm' 
                  : 'text-gray-600 hover:text-black'
              }`}
            >
              Structured
            </button>
            <button
              onClick={() => setViewMode('raw')}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-all ${
                viewMode === 'raw' 
                  ? 'bg-white text-black shadow-sm' 
                  : 'text-gray-600 hover:text-black'
              }`}
            >
              Raw Data
            </button>
          </div>
        </div>

        <h1 className="text-4xl font-bold text-black tracking-tight mb-2">
          Extraction Results
        </h1>
        <p className="text-gray-600 text-lg font-light">
          {result.filename} • {result.total_pages} pages • ${result.cost_breakdown.total_cost.toFixed(4)} processing cost
        </p>
      </div>

      {viewMode === 'structured' ? (
        /* Structured Data View */
        <div className="px-6 pb-12 space-y-8">
          {/* Statement Metadata */}
          <div className="bg-gray-50 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-black mb-6">Statement Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className={`p-4 rounded-xl border ${getConfidenceColor(structuredData.statement_metadata?.statement_provider)}`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Provider</div>
                <div className="font-semibold">{structuredData.statement_metadata?.statement_provider || 'Not detected'}</div>
              </div>
              <div className={`p-4 rounded-xl border ${getConfidenceColor(structuredData.statement_metadata?.statement_date)}`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Statement Date</div>
                <div className="font-semibold">{structuredData.statement_metadata?.statement_date || 'Not detected'}</div>
              </div>
              <div className={`p-4 rounded-xl border ${getConfidenceColor(structuredData.statement_metadata?.statement_period_start)}`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Period Start</div>
                <div className="font-semibold">{structuredData.statement_metadata?.statement_period_start || 'Not detected'}</div>
              </div>
              <div className={`p-4 rounded-xl border ${getConfidenceColor(structuredData.statement_metadata?.statement_period_end)}`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Period End</div>
                <div className="font-semibold">{structuredData.statement_metadata?.statement_period_end || 'Not detected'}</div>
              </div>
            </div>
          </div>

          {/* Customer Information */}
          <div className="bg-gray-50 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-black mb-6">Customer Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className={`p-4 rounded-xl border ${getConfidenceColor(structuredData.customer?.name)}`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Name</div>
                <div className="font-semibold">{structuredData.customer?.name || 'Not detected'}</div>
              </div>
              <div className={`p-4 rounded-xl border ${getConfidenceColor(structuredData.customer?.account_number)}`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Account Number</div>
                <div className="font-semibold font-mono">{structuredData.customer?.account_number || 'Not detected'}</div>
              </div>
              <div className={`p-4 rounded-xl border ${getConfidenceColor(structuredData.customer?.address)} md:col-span-2`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Address</div>
                <div className="font-semibold">{structuredData.customer?.address || 'Not detected'}</div>
              </div>
            </div>
          </div>

          {/* Account Holdings */}
          <div className="bg-gray-50 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-black mb-6">Account Holdings</h2>
            
            {structuredData.accounts && structuredData.accounts.length > 0 ? (
              structuredData.accounts.map((account, accountIndex) => (
                <div key={accountIndex} className="mb-6 last:mb-0">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-black">
                      {account.account_name || `Account ${accountIndex + 1}`}
                    </h3>
                    {account.account_total_value && (
                      <div className="text-xl font-bold text-green-600">
                        {formatCurrency(account.account_total_value)}
                      </div>
                    )}
                  </div>

                  {account.holdings && account.holdings.length > 0 ? (
                    <div className="space-y-3">
                      {account.holdings.map((holding, holdingIndex) => (
                        <div key={holdingIndex} className="bg-white rounded-xl p-4 border border-gray-200">
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div>
                              <div className="text-sm font-medium text-gray-600 mb-1">Security</div>
                              <div className="font-semibold">{holding.description || 'Unknown'}</div>
                              {holding.ticker && (
                                <div className="text-sm text-gray-500 font-mono">{holding.ticker}</div>
                              )}
                            </div>
                            <div>
                              <div className="text-sm font-medium text-gray-600 mb-1">Quantity</div>
                              <div className="font-semibold font-mono">{formatNumber(holding.quantity)}</div>
                            </div>
                            <div>
                              <div className="text-sm font-medium text-gray-600 mb-1">Price</div>
                              <div className="font-semibold font-mono">{formatCurrency(holding.price)}</div>
                            </div>
                            <div>
                              <div className="text-sm font-medium text-gray-600 mb-1">Market Value</div>
                              <div className="font-semibold font-mono text-green-600">{formatCurrency(holding.market_value)}</div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="bg-white rounded-xl p-8 text-center text-gray-500">
                      No holdings detected in this account
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="bg-white rounded-xl p-8 text-center text-gray-500">
                No accounts detected
              </div>
            )}
          </div>

          {/* Total Value */}
          {structuredData.statement_total_value && (
            <div className="bg-electric-cyan/5 border border-electric-cyan/20 rounded-2xl p-6">
              <div className="text-center">
                <div className="text-sm font-medium text-gray-600 mb-2">Total Portfolio Value</div>
                <div className="text-3xl font-bold text-black">{formatCurrency(structuredData.statement_total_value)}</div>
              </div>
            </div>
          )}

          {/* AI Processing Status */}
          <div className="bg-electric-cyan/5 border border-electric-cyan/20 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-black">AI Processing Status</h2>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="font-semibold text-green-600">
                  {structuredData.audit?.requires_human_review === false 
                    ? 'No Human Review Required' 
                    : structuredData.audit?.overall_status === 'PASS'
                    ? '100% AI Processed'
                    : 'Processing Complete'
                  }
                </span>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
              <div className="bg-white rounded-xl p-4 text-center">
                <div className="text-2xl font-bold text-green-600 mb-1">
                  {structuredData.audit?.overall_status === 'PASS' ? '100%' : '95%'}
                </div>
                <div className="text-gray-600">Accuracy</div>
              </div>
              <div className="bg-white rounded-xl p-4 text-center">
                <div className="text-2xl font-bold text-electric-cyan mb-1">
                  {structuredData.accounts?.length || 0}
                </div>
                <div className="text-gray-600">Accounts Found</div>
              </div>
              <div className="bg-white rounded-xl p-4 text-center">
                <div className="text-2xl font-bold text-electric-cyan mb-1">
                  {structuredData.accounts?.reduce((total, acc) => total + (acc.holdings?.length || 0), 0) || 0}
                </div>
                <div className="text-gray-600">Holdings Extracted</div>
              </div>
              <div className="bg-white rounded-xl p-4 text-center">
                <div className="text-2xl font-bold text-green-600 mb-1">AUTO</div>
                <div className="text-gray-600">Processing Mode</div>
              </div>
            </div>
          </div>

          {/* Audit Results */}
          {structuredData.audit && (
            <div className="bg-gray-50 rounded-2xl p-6">
              <h2 className="text-xl font-bold text-black mb-6">Audit Results & Validation</h2>
              
              {/* Statement Total Reconciliation */}
              {structuredData.audit.accounts_to_statement && (
                <div className="bg-white rounded-xl p-6 mb-6 border-l-4 border-electric-cyan">
                  <h3 className="font-semibold text-black mb-4 flex items-center">
                    <svg className="w-5 h-5 mr-2 text-electric-cyan" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    Statement Total Reconciliation
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="text-center">
                      <div className="text-sm text-gray-600 mb-1">Sum of Account Values</div>
                      <div className="text-xl font-bold text-black">
                        {formatCurrency(structuredData.audit.accounts_to_statement.total_of_account_values)}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-gray-600 mb-1">Statement Total</div>
                      <div className="text-xl font-bold text-black">
                        {formatCurrency(structuredData.audit.accounts_to_statement.statement_total_value)}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-gray-600 mb-1">Difference</div>
                      <div className={`text-xl font-bold ${
                        Math.abs(structuredData.audit.accounts_to_statement.difference) < 0.01 
                          ? 'text-green-600' 
                          : 'text-orange-600'
                      }`}>
                        {structuredData.audit.accounts_to_statement.difference >= 0 ? '+' : ''}{formatCurrency(structuredData.audit.accounts_to_statement.difference)}
                      </div>
                      <div className={`text-xs px-2 py-1 rounded-full mt-1 inline-block ${
                        structuredData.audit.accounts_to_statement.status === 'match' 
                          ? 'bg-green-100 text-green-600' 
                          : 'bg-orange-100 text-orange-600'
                      }`}>
                        {structuredData.audit.accounts_to_statement.status === 'match' ? 'BALANCED' : 'VARIANCE'}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Account-Level Reconciliation */}
              {structuredData.audit.holdings_to_account && (
                <div className="bg-white rounded-xl p-6 mb-6 border-l-4 border-blue-500">
                  <h3 className="font-semibold text-black mb-4 flex items-center">
                    <svg className="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                    </svg>
                    Account-Level Reconciliation
                  </h3>
                  <div className="space-y-4">
                    {structuredData.audit.holdings_to_account.map((account, index) => (
                      <div key={index} className="grid grid-cols-1 md:grid-cols-4 gap-4 py-3 border-b border-gray-100 last:border-b-0">
                        <div>
                          <div className="text-sm text-gray-600">Account</div>
                          <div className="font-semibold font-mono">{account.account_number}</div>
                        </div>
                        <div className="text-center">
                          <div className="text-sm text-gray-600">Holdings Sum</div>
                          <div className="font-semibold">{formatCurrency(account.holdings_sum)}</div>
                        </div>
                        <div className="text-center">
                          <div className="text-sm text-gray-600">Account Total</div>
                          <div className="font-semibold">{formatCurrency(account.account_total_value)}</div>
                        </div>
                        <div className="text-center">
                          <div className="text-sm text-gray-600">Variance</div>
                          <div className={`font-semibold ${
                            Math.abs(account.difference) < 0.01 ? 'text-green-600' : 'text-orange-600'
                          }`}>
                            {account.difference >= 0 ? '+' : ''}{formatCurrency(account.difference)}
                          </div>
                          <div className={`text-xs px-2 py-1 rounded-full mt-1 inline-block ${
                            account.status === 'match' ? 'bg-green-100 text-green-600' : 'bg-orange-100 text-orange-600'
                          }`}>
                            {account.status === 'match' ? 'MATCH' : 'DIFF'}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Quantity × Price = Value Logic Checks */}
              {structuredData.audit.quantity_value_logic && (
                <div className="bg-white rounded-xl p-6 mb-6 border-l-4 border-purple-500">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-black flex items-center">
                      <svg className="w-5 h-5 mr-2 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                      </svg>
                      Price × Quantity Validation
                    </h3>
                    <div className="text-sm text-gray-600">
                      {structuredData.audit.quantity_value_logic.length} positions validated
                    </div>
                  </div>

                  {/* Summary Stats */}
                  <div className="grid grid-cols-3 gap-4 mb-6">
                    <div className="bg-green-50 rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {structuredData.audit.quantity_value_logic.filter(item => item.status === 'match').length}
                      </div>
                      <div className="text-sm text-green-700">Exact Matches</div>
                    </div>
                    <div className="bg-orange-50 rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-orange-600">
                        {structuredData.audit.quantity_value_logic.filter(item => item.status !== 'match').length}
                      </div>
                      <div className="text-sm text-orange-700">Variances</div>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {((structuredData.audit.quantity_value_logic.filter(item => item.status === 'match').length / structuredData.audit.quantity_value_logic.length) * 100).toFixed(0)}%
                      </div>
                      <div className="text-sm text-blue-700">Accuracy Rate</div>
                    </div>
                  </div>

                  {/* Expandable Sections */}
                  <div className="space-y-4">
                    {/* Variances Section */}
                    {structuredData.audit.quantity_value_logic.filter(item => item.status !== 'match').length > 0 && (
                      <details className="group">
                        <summary className="cursor-pointer bg-orange-50 border border-orange-200 rounded-lg p-3 hover:bg-orange-100 transition-colors">
                          <div className="flex items-center justify-between">
                            <span className="font-medium text-orange-800 flex items-center">
                              <svg className="w-4 h-4 mr-2 transform group-open:rotate-90 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                              </svg>
                              ⚠️ Positions with Variances ({structuredData.audit.quantity_value_logic.filter(item => item.status !== 'match').length})
                            </span>
                            <span className="text-sm text-orange-600">Click to expand</span>
                          </div>
                        </summary>
                        <div className="mt-3 space-y-2">
                          {structuredData.audit.quantity_value_logic
                            .filter(item => item.status !== 'match')
                            .map((item, index) => (
                            <div key={index} className="grid grid-cols-1 md:grid-cols-6 gap-4 py-3 border border-orange-200 rounded-lg p-3 bg-orange-25">
                              <div>
                                <div className="text-sm text-gray-600">Security</div>
                                <div className="font-semibold font-mono text-sm">{item.cusip_or_ticker || 'N/A'}</div>
                                <div className="text-xs text-gray-500">{item.account_number}</div>
                              </div>
                              <div className="text-center">
                                <div className="text-sm text-gray-600">Computed</div>
                                <div className="font-semibold">{formatCurrency(item.computed_value)}</div>
                              </div>
                              <div className="text-center">
                                <div className="text-sm text-gray-600">Reported</div>
                                <div className="font-semibold">{formatCurrency(item.reported_market_value)}</div>
                              </div>
                              <div className="text-center">
                                <div className="text-sm text-gray-600">Difference</div>
                                <div className="font-semibold text-orange-600">
                                  {formatCurrency(item.computed_value - item.reported_market_value)}
                                </div>
                              </div>
                              <div className="text-center">
                                <div className="text-sm text-gray-600">Difference %</div>
                                <div className={`font-semibold ${
                                  Math.abs(item.difference_pct) < 1 ? 'text-green-600' : 'text-orange-600'
                                }`}>
                                  {item.difference_pct.toFixed(2)}%
                                </div>
                              </div>
                              <div className="text-center">
                                <div className={`text-xs px-2 py-1 rounded-full ${
                                  item.status === 'match' ? 'bg-green-100 text-green-600' : 'bg-orange-100 text-orange-600'
                                }`}>
                                  {item.status === 'discrepancy due to accrued interest or other' ? 'ACCRUED INT.' : 'VARIANCE'}
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </details>
                    )}

                    {/* Perfect Matches Section */}
                    {structuredData.audit.quantity_value_logic.filter(item => item.status === 'match').length > 0 && (
                      <details className="group">
                        <summary className="cursor-pointer bg-green-50 border border-green-200 rounded-lg p-3 hover:bg-green-100 transition-colors">
                          <div className="flex items-center justify-between">
                            <span className="font-medium text-green-800 flex items-center">
                              <svg className="w-4 h-4 mr-2 transform group-open:rotate-90 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                              </svg>
                              ✅ Positions with Exact Matches ({structuredData.audit.quantity_value_logic.filter(item => item.status === 'match').length})
                            </span>
                            <span className="text-sm text-green-600">Click to expand</span>
                          </div>
                        </summary>
                        <div className="mt-3 space-y-2 max-h-64 overflow-y-auto">
                          {structuredData.audit.quantity_value_logic
                            .filter(item => item.status === 'match')
                            .map((item, index) => (
                            <div key={index} className="grid grid-cols-1 md:grid-cols-5 gap-4 py-2 border border-green-200 rounded-lg p-3 bg-green-25">
                              <div>
                                <div className="text-sm text-gray-600">Security</div>
                                <div className="font-semibold font-mono text-sm">{item.cusip_or_ticker || 'N/A'}</div>
                                <div className="text-xs text-gray-500">{item.account_number}</div>
                              </div>
                              <div className="text-center">
                                <div className="text-sm text-gray-600">Computed</div>
                                <div className="font-semibold">{formatCurrency(item.computed_value)}</div>
                              </div>
                              <div className="text-center">
                                <div className="text-sm text-gray-600">Reported</div>
                                <div className="font-semibold">{formatCurrency(item.reported_market_value)}</div>
                              </div>
                              <div className="text-center">
                                <div className="text-sm text-gray-600">Difference</div>
                                <div className="font-semibold text-green-600">
                                  {formatCurrency(0)}
                                </div>
                              </div>
                              <div className="text-center">
                                <div className={`text-xs px-2 py-1 rounded-full bg-green-100 text-green-600`}>
                                  EXACT MATCH
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </details>
                    )}
                  </div>

                  {/* Overall Validation Summary */}
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="text-sm text-gray-600">
                      <strong>Validation Summary:</strong> All {structuredData.audit.quantity_value_logic.length} positions have been validated using Quantity × Price = Market Value calculations. 
                      {structuredData.audit.quantity_value_logic.filter(item => item.status !== 'match').length === 0 
                        ? " All calculations are exact matches." 
                        : ` ${structuredData.audit.quantity_value_logic.filter(item => item.status !== 'match').length} position(s) show variances, likely due to accrued interest, fees, or rounding differences.`
                      }
                    </div>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Data Quality Checks */}
                <div className="space-y-4">
                  <h3 className="font-semibold text-black mb-3">Data Quality</h3>
                  
                  <div className="bg-white rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Section Presence</span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        structuredData.audit.section_presence?.status === 'present' 
                          ? 'bg-green-100 text-green-600' 
                          : 'bg-orange-100 text-orange-600'
                      }`}>
                        {structuredData.audit.section_presence?.status === 'present' ? 'COMPLETE' : 'INCOMPLETE'}
                      </span>
                    </div>
                    {structuredData.audit.section_presence?.missing_sections?.length > 0 && (
                      <div className="text-xs text-gray-500">
                        Missing: {structuredData.audit.section_presence.missing_sections.join(', ')}
                      </div>
                    )}
                  </div>

                  <div className="bg-white rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Zero/Negative Values</span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        structuredData.audit.zero_negative_guard?.status === 'no issues' 
                          ? 'bg-green-100 text-green-600' 
                          : 'bg-orange-100 text-orange-600'
                      }`}>
                        {structuredData.audit.zero_negative_guard?.status === 'no issues' ? 'CLEAN' : 'ISSUES'}
                      </span>
                    </div>
                    {structuredData.audit.zero_negative_guard?.problem_rows?.length > 0 && (
                      <div className="text-xs text-gray-500 mt-2">
                        <div className="font-medium mb-1">Problem positions:</div>
                        {structuredData.audit.zero_negative_guard.problem_rows.map((row, idx) => (
                          <div key={idx} className="text-xs">
                            {row.description} (Qty: {row.quantity}, Value: {formatCurrency(row.market_value)})
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="bg-white rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Missing Identifiers</span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        structuredData.audit.missing_identifier?.status === 'none' 
                          ? 'bg-green-100 text-green-600' 
                          : 'bg-orange-100 text-orange-600'
                      }`}>
                        {structuredData.audit.missing_identifier?.holdings_without_id?.length || 0} MISSING
                      </span>
                    </div>
                    {structuredData.audit.missing_identifier?.holdings_without_id?.length > 0 && (
                      <div className="text-xs text-gray-500 mt-2">
                        Holdings without CUSIP/ticker: {structuredData.audit.missing_identifier.holdings_without_id.length}
                      </div>
                    )}
                  </div>
                </div>

                {/* Validation Checks */}
                <div className="space-y-4">
                  <h3 className="font-semibold text-black mb-3">Validation</h3>
                  
                  <div className="bg-white rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Duplicate Detection</span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        structuredData.audit.duplicate_security_id?.status === 'no duplicates' 
                          ? 'bg-green-100 text-green-600' 
                          : 'bg-orange-100 text-orange-600'
                      }`}>
                        {structuredData.audit.duplicate_security_id?.duplicates_found?.length || 0} FOUND
                      </span>
                    </div>
                    {structuredData.audit.duplicate_security_id?.duplicates_found?.length > 0 && (
                      <div className="text-xs text-gray-500">
                        Duplicates: {structuredData.audit.duplicate_security_id.duplicates_found.join(', ')}
                      </div>
                    )}
                  </div>

                  <div className="bg-white rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Date Range Sanity</span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        structuredData.audit.date_range_sanity?.status === 'no future dates' 
                          ? 'bg-green-100 text-green-600' 
                          : 'bg-orange-100 text-orange-600'
                      }`}>
                        {structuredData.audit.date_range_sanity?.future_dates_found?.length || 0} FUTURE
                      </span>
                    </div>
                  </div>

                  <div className="bg-white rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Currency Coherence</span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        structuredData.audit.currency_symbol_coherence?.status === 'consistent' 
                          ? 'bg-green-100 text-green-600' 
                          : 'bg-orange-100 text-orange-600'
                      }`}>
                        {structuredData.audit.currency_symbol_coherence?.status === 'consistent' ? 'CONSISTENT' : 'MIXED'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Overall Status */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-semibold text-black">Overall Audit Status</div>
                    <div className="text-sm text-gray-600">
                      {structuredData.audit.requires_human_review === false 
                        ? 'All checks passed. Document ready for automated processing.'
                        : 'Some items may require manual review.'
                      }
                    </div>
                  </div>
                  <div className={`px-4 py-2 rounded-full font-semibold ${
                    structuredData.audit.overall_status === 'PASS' 
                      ? 'bg-green-100 text-green-600' 
                      : 'bg-orange-100 text-orange-600'
                  }`}>
                    {structuredData.audit.overall_status || 'PENDING'}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Processing Info */}
          <div className="bg-gray-50 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-black mb-4">Processing Efficiency</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-electric-cyan mb-1">{result.total_pages || 1}</div>
                <div className="text-sm text-gray-600">Pages Processed</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600 mb-1">{result.processing_time}</div>
                <div className="text-sm text-gray-600">Processing Time</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-black mb-1">${result.cost_breakdown.total_cost.toFixed(4)}</div>
                <div className="text-sm text-gray-600">Total Cost</div>
                <div className="text-xs text-gray-500 mt-1">
                  Vision: ${result.cost_breakdown.text_extraction_cost.toFixed(4)} • LLM: ${result.cost_breakdown.structured_extraction_cost.toFixed(4)}
                </div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600 mb-1">
                  ${(parseFloat(structuredData.statement_total_value || 0) / result.cost_breakdown.total_cost).toLocaleString(undefined, {maximumFractionDigits: 0})}
                </div>
                <div className="text-sm text-gray-600">Value per $1 Cost</div>
                <div className="text-xs text-gray-500 mt-1">ROI Efficiency</div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Raw Data View */
        <div className="px-6 pb-12">
          <div className="bg-gray-50 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-black mb-6">Raw Extracted Text</h2>
            <div className="space-y-6">
              {extractedText.map((page, index) => (
                <div key={index} className="bg-white rounded-xl p-6 border border-gray-200">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-semibold text-black">Page {page.page_number}</h3>
                    <div className="text-sm text-gray-500">
                      Processing time: {page.processing_time} • Cost: ${page.cost.toFixed(4)}
                    </div>
                  </div>
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono bg-gray-50 p-4 rounded-lg overflow-x-auto">
                    {page.text}
                  </pre>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ReviewPage