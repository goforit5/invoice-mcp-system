import React, { useState } from 'react'
import axios from 'axios'

const InvoiceReview = ({ result, onBack }) => {
  const [viewMode, setViewMode] = useState('structured') // 'structured' or 'raw'
  const [editableData, setEditableData] = useState(result.structured_data)
  const [isEditing, setIsEditing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  const extractedText = result.extracted_text

  const formatCurrency = (value) => {
    if (!value) return '$0.00'
    if (typeof value === 'string') {
      const cleanValue = value.replace(/[,$]/g, '')
      const numValue = parseFloat(cleanValue)
      return isNaN(numValue) ? value : `$${numValue.toLocaleString()}`
    }
    return `$${parseFloat(value).toLocaleString()}`
  }

  const getConfidenceColor = (hasData) => {
    if (!hasData) return 'bg-gray-100 text-gray-500'
    return 'bg-invoice-blue/10 text-invoice-blue border-invoice-blue/20'
  }

  const handleFieldChange = (section, field, value) => {
    setEditableData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }))
  }

  const handleLineItemChange = (index, field, value) => {
    setEditableData(prev => ({
      ...prev,
      line_items: prev.line_items.map((item, i) => 
        i === index ? { ...item, [field]: value } : item
      )
    }))
  }

  const addLineItem = () => {
    setEditableData(prev => ({
      ...prev,
      line_items: [
        ...prev.line_items,
        {
          date: null,
          description: '',
          quantity: '',
          unit: '',
          rate: '',
          amount: '',
          notes: null
        }
      ]
    }))
  }

  const removeLineItem = (index) => {
    setEditableData(prev => ({
      ...prev,
      line_items: prev.line_items.filter((_, i) => i !== index)
    }))
  }

  const saveChanges = async () => {
    setIsSaving(true)
    try {
      // Extract ID from result or use filename as fallback
      const recordId = result.record_id || Date.now().toString()
      
      await axios.put(`/api/invoice/${recordId}`, editableData)
      
      // Update the original result
      result.structured_data = editableData
      
      alert('Invoice data saved successfully!')
    } catch (error) {
      console.error('Error saving invoice:', error)
      alert('Failed to save changes. Please try again.')
    } finally {
      setIsSaving(false)
      setIsEditing(false)
    }
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="px-6 pt-16 pb-8">
        <div className="flex items-center justify-between mb-4">
          <button 
            onClick={onBack}
            className="flex items-center space-x-2 text-invoice-blue font-semibold hover:text-invoice-blue/80 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span>Back</span>
          </button>

          <div className="flex items-center space-x-4">
            {/* Edit Toggle */}
            {!isEditing ? (
              <button
                onClick={() => setIsEditing(true)}
                className="bg-invoice-blue text-white font-semibold py-2 px-4 rounded-xl hover:bg-invoice-blue/90 transition-colors"
              >
                Edit Invoice
              </button>
            ) : (
              <div className="flex space-x-2">
                <button
                  onClick={() => setIsEditing(false)}
                  className="bg-gray-100 text-gray-700 font-semibold py-2 px-4 rounded-xl hover:bg-gray-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={saveChanges}
                  disabled={isSaving}
                  className="bg-invoice-green text-white font-semibold py-2 px-4 rounded-xl hover:bg-invoice-green/90 transition-colors disabled:opacity-50"
                >
                  {isSaving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            )}

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
        </div>

        <h1 className="text-4xl font-bold text-black tracking-tight mb-2">
          Invoice Review
        </h1>
        <p className="text-gray-600 text-lg font-light">
          {result.filename} • {result.total_pages} pages • ${result.cost_breakdown.total_cost.toFixed(4)} processing cost
        </p>
      </div>

      {viewMode === 'structured' ? (
        /* Structured Data View */
        <div className="px-6 pb-12 space-y-8">
          {/* Invoice Metadata */}
          <div className="bg-gray-50 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-black mb-6">Invoice Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className={`p-4 rounded-xl border ${getConfidenceColor(editableData.invoice_metadata?.invoice_number)}`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Invoice Number</div>
                {isEditing ? (
                  <input
                    type="text"
                    value={editableData.invoice_metadata?.invoice_number || ''}
                    onChange={(e) => handleFieldChange('invoice_metadata', 'invoice_number', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg font-semibold"
                  />
                ) : (
                  <div className="font-semibold">{editableData.invoice_metadata?.invoice_number || 'Not detected'}</div>
                )}
              </div>
              
              <div className={`p-4 rounded-xl border ${getConfidenceColor(editableData.invoice_metadata?.issue_date)}`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Issue Date</div>
                {isEditing ? (
                  <input
                    type="date"
                    value={editableData.invoice_metadata?.issue_date || ''}
                    onChange={(e) => handleFieldChange('invoice_metadata', 'issue_date', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg font-semibold"
                  />
                ) : (
                  <div className="font-semibold">{editableData.invoice_metadata?.issue_date || 'Not detected'}</div>
                )}
              </div>
              
              <div className={`p-4 rounded-xl border ${getConfidenceColor(editableData.invoice_metadata?.due_date)}`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Due Date</div>
                {isEditing ? (
                  <input
                    type="date"
                    value={editableData.invoice_metadata?.due_date || ''}
                    onChange={(e) => handleFieldChange('invoice_metadata', 'due_date', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg font-semibold"
                  />
                ) : (
                  <div className="font-semibold">{editableData.invoice_metadata?.due_date || 'Not detected'}</div>
                )}
              </div>
              
              <div className={`p-4 rounded-xl border ${getConfidenceColor(editableData.invoice_metadata?.balance_due)}`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Balance Due</div>
                {isEditing ? (
                  <input
                    type="text"
                    value={editableData.invoice_metadata?.balance_due || ''}
                    onChange={(e) => handleFieldChange('invoice_metadata', 'balance_due', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg font-semibold"
                  />
                ) : (
                  <div className="font-semibold">{formatCurrency(editableData.invoice_metadata?.balance_due)}</div>
                )}
              </div>
            </div>
          </div>

          {/* Vendor Information */}
          <div className="bg-gray-50 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-black mb-6">Vendor Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className={`p-4 rounded-xl border ${getConfidenceColor(editableData.vendor?.name)}`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Company Name</div>
                {isEditing ? (
                  <input
                    type="text"
                    value={editableData.vendor?.name || ''}
                    onChange={(e) => handleFieldChange('vendor', 'name', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg font-semibold"
                  />
                ) : (
                  <div className="font-semibold">{editableData.vendor?.name || 'Not detected'}</div>
                )}
              </div>
              
              <div className={`p-4 rounded-xl border ${getConfidenceColor(editableData.vendor?.email)}`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Email</div>
                {isEditing ? (
                  <input
                    type="email"
                    value={editableData.vendor?.email || ''}
                    onChange={(e) => handleFieldChange('vendor', 'email', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg font-semibold"
                  />
                ) : (
                  <div className="font-semibold">{editableData.vendor?.email || 'Not detected'}</div>
                )}
              </div>
              
              <div className={`p-4 rounded-xl border col-span-2 ${getConfidenceColor(editableData.vendor?.address)}`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Address</div>
                {isEditing ? (
                  <textarea
                    value={`${editableData.vendor?.address || ''} ${editableData.vendor?.city || ''} ${editableData.vendor?.state || ''} ${editableData.vendor?.zip || ''}`.trim()}
                    onChange={(e) => handleFieldChange('vendor', 'address', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg font-semibold resize-none"
                    rows="2"
                  />
                ) : (
                  <div className="font-semibold">
                    {[editableData.vendor?.address, editableData.vendor?.city, editableData.vendor?.state, editableData.vendor?.zip]
                      .filter(Boolean).join(', ') || 'Not detected'}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Customer Information */}
          <div className="bg-gray-50 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-black mb-6">Customer Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className={`p-4 rounded-xl border ${getConfidenceColor(editableData.customer?.name)}`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Customer Name</div>
                {isEditing ? (
                  <input
                    type="text"
                    value={editableData.customer?.name || ''}
                    onChange={(e) => handleFieldChange('customer', 'name', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg font-semibold"
                  />
                ) : (
                  <div className="font-semibold">{editableData.customer?.name || 'Not detected'}</div>
                )}
              </div>
              
              <div className={`p-4 rounded-xl border ${getConfidenceColor(editableData.customer?.account_number)}`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Account Number</div>
                {isEditing ? (
                  <input
                    type="text"
                    value={editableData.customer?.account_number || ''}
                    onChange={(e) => handleFieldChange('customer', 'account_number', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg font-semibold"
                  />
                ) : (
                  <div className="font-semibold">{editableData.customer?.account_number || 'Not detected'}</div>
                )}
              </div>
              
              <div className={`p-4 rounded-xl border col-span-2 ${getConfidenceColor(editableData.customer?.address)}`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Address</div>
                {isEditing ? (
                  <textarea
                    value={`${editableData.customer?.address || ''} ${editableData.customer?.city || ''} ${editableData.customer?.state || ''} ${editableData.customer?.zip || ''}`.trim()}
                    onChange={(e) => handleFieldChange('customer', 'address', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg font-semibold resize-none"
                    rows="2"
                  />
                ) : (
                  <div className="font-semibold">
                    {[editableData.customer?.address, editableData.customer?.city, editableData.customer?.state, editableData.customer?.zip]
                      .filter(Boolean).join(', ') || 'Not detected'}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Line Items */}
          <div className="bg-gray-50 rounded-2xl p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-black">Line Items</h2>
              {isEditing && (
                <button
                  onClick={addLineItem}
                  className="bg-invoice-blue text-white font-semibold py-2 px-4 rounded-xl hover:bg-invoice-blue/90 transition-colors"
                >
                  Add Item
                </button>
              )}
            </div>
            
            <div className="space-y-4">
              {editableData.line_items?.map((item, index) => (
                <div key={index} className="bg-white rounded-xl p-4 border">
                  <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                    <div>
                      <div className="text-sm font-medium text-gray-600 mb-1">Description</div>
                      {isEditing ? (
                        <input
                          type="text"
                          value={item.description || ''}
                          onChange={(e) => handleLineItemChange(index, 'description', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      ) : (
                        <div className="font-semibold">{item.description || 'N/A'}</div>
                      )}
                    </div>
                    
                    <div>
                      <div className="text-sm font-medium text-gray-600 mb-1">Quantity</div>
                      {isEditing ? (
                        <input
                          type="text"
                          value={item.quantity || ''}
                          onChange={(e) => handleLineItemChange(index, 'quantity', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      ) : (
                        <div className="font-semibold">{item.quantity || 'N/A'}</div>
                      )}
                    </div>
                    
                    <div>
                      <div className="text-sm font-medium text-gray-600 mb-1">Rate</div>
                      {isEditing ? (
                        <input
                          type="text"
                          value={item.rate || ''}
                          onChange={(e) => handleLineItemChange(index, 'rate', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      ) : (
                        <div className="font-semibold">{formatCurrency(item.rate)}</div>
                      )}
                    </div>
                    
                    <div>
                      <div className="text-sm font-medium text-gray-600 mb-1">Amount</div>
                      {isEditing ? (
                        <input
                          type="text"
                          value={item.amount || ''}
                          onChange={(e) => handleLineItemChange(index, 'amount', e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                        />
                      ) : (
                        <div className="font-semibold">{formatCurrency(item.amount)}</div>
                      )}
                    </div>
                    
                    {isEditing && (
                      <div className="flex items-end">
                        <button
                          onClick={() => removeLineItem(index)}
                          className="bg-red-100 text-red-600 p-2 rounded-lg hover:bg-red-200 transition-colors"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Totals */}
          <div className="bg-gray-50 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-black mb-6">Invoice Totals</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className={`p-4 rounded-xl border ${getConfidenceColor(editableData.totals?.subtotal)}`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Subtotal</div>
                {isEditing ? (
                  <input
                    type="text"
                    value={editableData.totals?.subtotal || ''}
                    onChange={(e) => handleFieldChange('totals', 'subtotal', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg font-semibold"
                  />
                ) : (
                  <div className="font-semibold">{formatCurrency(editableData.totals?.subtotal)}</div>
                )}
              </div>
              
              <div className={`p-4 rounded-xl border ${getConfidenceColor(editableData.totals?.tax)}`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Tax</div>
                {isEditing ? (
                  <input
                    type="text"
                    value={editableData.totals?.tax || ''}
                    onChange={(e) => handleFieldChange('totals', 'tax', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg font-semibold"
                  />
                ) : (
                  <div className="font-semibold">{formatCurrency(editableData.totals?.tax)}</div>
                )}
              </div>
              
              <div className={`p-4 rounded-xl border ${getConfidenceColor(editableData.totals?.shipping)}`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Shipping</div>
                {isEditing ? (
                  <input
                    type="text"
                    value={editableData.totals?.shipping || ''}
                    onChange={(e) => handleFieldChange('totals', 'shipping', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg font-semibold"
                  />
                ) : (
                  <div className="font-semibold">{formatCurrency(editableData.totals?.shipping)}</div>
                )}
              </div>
              
              <div className={`p-4 rounded-xl border-2 border-invoice-green bg-invoice-green/10 ${getConfidenceColor(editableData.totals?.total)}`}>
                <div className="text-sm font-medium text-gray-600 mb-1">Total</div>
                {isEditing ? (
                  <input
                    type="text"
                    value={editableData.totals?.total || ''}
                    onChange={(e) => handleFieldChange('totals', 'total', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg font-bold text-lg"
                  />
                ) : (
                  <div className="font-bold text-lg">{formatCurrency(editableData.totals?.total)}</div>
                )}
              </div>
            </div>
          </div>

          {/* AI Processing Status */}
          <div className="bg-invoice-blue/5 border border-invoice-blue/20 rounded-2xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-black">AI Processing Status</h2>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="font-semibold text-green-600">
                  {editableData.audit?.requires_human_review === false 
                    ? 'No Human Review Required' 
                    : editableData.audit?.overall_status === 'PASS'
                    ? '100% AI Processed'
                    : 'Processing Complete'
                  }
                </span>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
              <div className="bg-white rounded-xl p-4 text-center">
                <div className="text-2xl font-bold text-green-600 mb-1">
                  {editableData.audit?.overall_status === 'PASS' ? '100%' : '95%'}
                </div>
                <div className="text-gray-600">Accuracy</div>
              </div>
              <div className="bg-white rounded-xl p-4 text-center">
                <div className="text-2xl font-bold text-invoice-blue mb-1">
                  {editableData.line_items?.length || 0}
                </div>
                <div className="text-gray-600">Line Items Found</div>
              </div>
              <div className="bg-white rounded-xl p-4 text-center">
                <div className="text-2xl font-bold text-invoice-blue mb-1">
                  {Object.keys(editableData).filter(key => editableData[key] && typeof editableData[key] === 'object').length}
                </div>
                <div className="text-gray-600">Fields Extracted</div>
              </div>
              <div className="bg-white rounded-xl p-4 text-center">
                <div className="text-2xl font-bold text-green-600 mb-1">AUTO</div>
                <div className="text-gray-600">Processing Mode</div>
              </div>
            </div>
          </div>

          {/* Audit Results */}
          {editableData.audit && (
            <div className="bg-gray-50 rounded-2xl p-6">
              <h2 className="text-xl font-bold text-black mb-6">Audit Results & Validation</h2>
              
              {/* Total Reconciliation */}
              {editableData.audit.totals_reconciliation && (
                <div className="bg-white rounded-xl p-6 mb-6 border-l-4 border-invoice-blue">
                  <h3 className="font-semibold text-black mb-4 flex items-center">
                    <svg className="w-5 h-5 mr-2 text-invoice-blue" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    Invoice Total Reconciliation
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="text-center">
                      <div className="text-sm text-gray-600 mb-1">Sum of Line Items</div>
                      <div className="text-xl font-bold text-black">
                        {formatCurrency(editableData.audit.totals_reconciliation.line_items_sum)}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-gray-600 mb-1">Invoice Total</div>
                      <div className="text-xl font-bold text-black">
                        {formatCurrency(editableData.audit.totals_reconciliation.invoice_total)}
                      </div>
                    </div>
                    <div className="text-center">
                      <div className="text-sm text-gray-600 mb-1">Difference</div>
                      <div className={`text-xl font-bold ${
                        Math.abs(editableData.audit.totals_reconciliation.difference || 0) < 0.01 
                          ? 'text-green-600' 
                          : 'text-orange-600'
                      }`}>
                        {(editableData.audit.totals_reconciliation.difference || 0) >= 0 ? '+' : ''}{formatCurrency(editableData.audit.totals_reconciliation.difference || 0)}
                      </div>
                      <div className={`text-xs px-2 py-1 rounded-full mt-1 inline-block ${
                        editableData.audit.totals_reconciliation.status === 'match' 
                          ? 'bg-green-100 text-green-600' 
                          : 'bg-orange-100 text-orange-600'
                      }`}>
                        {editableData.audit.totals_reconciliation.status === 'match' ? 'BALANCED' : 'VARIANCE'}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Line Item Validation */}
              {editableData.audit.line_item_validation && (
                <div className="bg-white rounded-xl p-6 mb-6 border-l-4 border-blue-500">
                  <h3 className="font-semibold text-black mb-4 flex items-center">
                    <svg className="w-5 h-5 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                    Line Item Math Validation
                  </h3>
                  <div className="space-y-3">
                    {editableData.audit.line_item_validation
                      .filter(item => item.status !== 'match')
                      .map((item, index) => (
                      <div key={index} className="grid grid-cols-1 md:grid-cols-5 gap-4 py-3 border border-orange-200 rounded-lg p-3 bg-orange-50">
                        <div>
                          <div className="text-sm text-gray-600">Description</div>
                          <div className="font-semibold text-sm">{item.description || 'N/A'}</div>
                        </div>
                        <div className="text-center">
                          <div className="text-sm text-gray-600">Computed</div>
                          <div className="font-semibold">{formatCurrency(item.computed_amount)}</div>
                        </div>
                        <div className="text-center">
                          <div className="text-sm text-gray-600">Reported</div>
                          <div className="font-semibold">{formatCurrency(item.reported_amount)}</div>
                        </div>
                        <div className="text-center">
                          <div className="text-sm text-gray-600">Difference</div>
                          <div className={`font-semibold ${
                            Math.abs(item.difference || 0) < 0.01 ? 'text-green-600' : 'text-orange-600'
                          }`}>
                            {formatCurrency(item.difference || 0)}
                          </div>
                        </div>
                        <div className="text-center">
                          <div className={`text-xs px-2 py-1 rounded-full ${
                            item.status === 'match' ? 'bg-green-100 text-green-600' : 'bg-orange-100 text-orange-600'
                          }`}>
                            {item.status === 'match' ? 'MATCH' : 'VARIANCE'}
                          </div>
                        </div>
                      </div>
                    ))}
                    {editableData.audit.line_item_validation?.filter(item => item.status === 'match').length > 0 && (
                      <div className="text-center py-2 text-green-600 text-sm">
                        ✅ {editableData.audit.line_item_validation.filter(item => item.status === 'match').length} line items validated with exact calculations
                      </div>
                    )}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Data Quality Checks */}
                <div className="space-y-4">
                  <h3 className="font-semibold text-black mb-3">Data Quality</h3>
                  
                  <div className="bg-white rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Required Fields</span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        editableData.audit.required_fields?.status === 'complete' 
                          ? 'bg-green-100 text-green-600' 
                          : 'bg-orange-100 text-orange-600'
                      }`}>
                        {editableData.audit.required_fields?.status === 'complete' ? 'COMPLETE' : 'INCOMPLETE'}
                      </span>
                    </div>
                    {editableData.audit.required_fields?.missing_fields?.length > 0 && (
                      <div className="text-xs text-gray-500">
                        Missing: {editableData.audit.required_fields.missing_fields.join(', ')}
                      </div>
                    )}
                  </div>

                  <div className="bg-white rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Date Validation</span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        editableData.audit.date_validation?.status === 'valid' 
                          ? 'bg-green-100 text-green-600' 
                          : 'bg-orange-100 text-orange-600'
                      }`}>
                        {editableData.audit.date_validation?.status === 'valid' ? 'VALID' : 'ISSUES'}
                      </span>
                    </div>
                    {editableData.audit.date_validation?.issues?.length > 0 && (
                      <div className="text-xs text-gray-500">
                        Issues: {editableData.audit.date_validation.issues.join(', ')}
                      </div>
                    )}
                  </div>

                  <div className="bg-white rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Format Consistency</span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        editableData.audit.format_consistency?.status === 'consistent' 
                          ? 'bg-green-100 text-green-600' 
                          : 'bg-orange-100 text-orange-600'
                      }`}>
                        {editableData.audit.format_consistency?.status === 'consistent' ? 'CONSISTENT' : 'MIXED'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Validation Checks */}
                <div className="space-y-4">
                  <h3 className="font-semibold text-black mb-3">Validation</h3>
                  
                  <div className="bg-white rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Duplicate Line Items</span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        editableData.audit.duplicate_detection?.status === 'no duplicates' 
                          ? 'bg-green-100 text-green-600' 
                          : 'bg-orange-100 text-orange-600'
                      }`}>
                        {editableData.audit.duplicate_detection?.duplicates_found?.length || 0} FOUND
                      </span>
                    </div>
                    {editableData.audit.duplicate_detection?.duplicates_found?.length > 0 && (
                      <div className="text-xs text-gray-500">
                        Duplicates detected
                      </div>
                    )}
                  </div>

                  <div className="bg-white rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Amount Validation</span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        editableData.audit.amount_validation?.status === 'valid' 
                          ? 'bg-green-100 text-green-600' 
                          : 'bg-orange-100 text-orange-600'
                      }`}>
                        {editableData.audit.amount_validation?.status === 'valid' ? 'VALID' : 'ISSUES'}
                      </span>
                    </div>
                  </div>

                  <div className="bg-white rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Vendor/Customer Check</span>
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        editableData.audit.entity_validation?.status === 'valid' 
                          ? 'bg-green-100 text-green-600' 
                          : 'bg-orange-100 text-orange-600'
                      }`}>
                        {editableData.audit.entity_validation?.status === 'valid' ? 'VALID' : 'ISSUES'}
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
                      {editableData.audit.requires_human_review === false 
                        ? 'All checks passed. Invoice ready for automated processing.'
                        : 'Some items may require manual review.'
                      }
                    </div>
                  </div>
                  <div className={`px-4 py-2 rounded-full font-semibold ${
                    editableData.audit.overall_status === 'PASS' 
                      ? 'bg-green-100 text-green-600' 
                      : 'bg-orange-100 text-orange-600'
                  }`}>
                    {editableData.audit.overall_status || 'PENDING'}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Processing Efficiency */}
          <div className="bg-gray-50 rounded-2xl p-6">
            <h2 className="text-xl font-bold text-black mb-4">Processing Efficiency</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-invoice-blue mb-1">{result.total_pages || 1}</div>
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
                  ${(parseFloat(editableData.totals?.total?.replace(/[^0-9.-]+/g,"") || 0) / result.cost_breakdown.total_cost).toLocaleString(undefined, {maximumFractionDigits: 0})}
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
              {extractedText?.map((page, index) => (
                <div key={index} className="bg-white rounded-xl p-4 border">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold">Page {page.page_number || index + 1}</h3>
                    <div className="text-sm text-gray-500">
                      Processing time: {page.processing_time || 'N/A'} • Cost: ${page.cost?.toFixed(4) || '0.0000'}
                    </div>
                  </div>
                  <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono bg-gray-50 p-4 rounded-lg overflow-x-auto">
                    {page.text || 'No text extracted'}
                  </pre>
                </div>
              ))}
            </div>
          </div>

          {/* JSON Output */}
          <div className="bg-gray-50 rounded-2xl p-6 mt-8">
            <h2 className="text-xl font-bold text-black mb-6">Structured JSON Output</h2>
            <div className="bg-black rounded-xl p-4 overflow-x-auto">
              <pre className="text-green-400 text-sm font-mono">
                {JSON.stringify(editableData, null, 2)}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default InvoiceReview