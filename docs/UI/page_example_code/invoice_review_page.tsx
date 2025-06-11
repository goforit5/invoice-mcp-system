import React, { useState, useEffect } from 'react';
import { ChevronLeft, Check, X, RotateCcw, ZoomIn, ZoomOut, Edit3, AlertCircle, CheckCircle2 } from 'lucide-react';

const InvoiceReview = () => {
  const [zoomLevel, setZoomLevel] = useState(1);
  const [selectedField, setSelectedField] = useState(null);
  const [editingField, setEditingField] = useState(null);
  const [showingLearning, setShowingLearning] = useState(false);
  const [formData, setFormData] = useState({
    vendor: { value: "Acme Corporation", confidence: 95, verified: true },
    amount: { value: "2,450.00", confidence: 88, verified: false },
    invoiceNumber: { value: "INV-2024-001", confidence: 92, verified: true },
    date: { value: "March 15, 2024", confidence: 85, verified: false },
    dueDate: { value: "April 14, 2024", confidence: 78, verified: false },
    description: { value: "Professional Services - Q1 2024", confidence: 70, verified: false }
  });

  const handleFieldEdit = (fieldName, newValue) => {
    setFormData(prev => ({
      ...prev,
      [fieldName]: {
        ...prev[fieldName],
        value: newValue,
        confidence: 100, // Manual entry = 100% confidence
        verified: true
      }
    }));
    
    // Show learning feedback
    setShowingLearning(true);
    setTimeout(() => setShowingLearning(false), 2000);
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 90) return 'bg-blue-50 border-blue-200';
    if (confidence >= 70) return 'bg-blue-25 border-blue-100';
    return 'bg-orange-25 border-orange-200';
  };

  const getConfidenceIndicator = (confidence, verified) => {
    if (verified) return 'bg-green-500';
    if (confidence >= 90) return 'bg-blue-500';
    if (confidence >= 70) return 'bg-blue-400';
    return 'bg-orange-400';
  };

  const allFieldsVerified = Object.values(formData).every(field => field.verified);

  return (
    <div className="min-h-screen bg-white">
      
      {/* Header */}
      <div className="bg-white border-b border-gray-100">
        <div className="flex items-center justify-between px-6 py-4 pt-16">
          <button className="flex items-center space-x-2">
            <ChevronLeft className="w-6 h-6 text-blue-500" />
            <span className="text-blue-500 font-medium">Back</span>
          </button>
          
          <h1 className="text-lg font-semibold text-black">Review Invoice</h1>
          
          <button className="w-8 h-8 flex items-center justify-center">
            <RotateCcw className="w-5 h-5 text-gray-400" />
          </button>
        </div>
      </div>

      {/* Split View Container */}
      <div className="flex-1 lg:flex">
        
        {/* Document Preview */}
        <div className="lg:w-2/5 bg-gray-50 relative">
          <div className="sticky top-0 h-80 lg:h-screen flex items-center justify-center p-6">
            
            {/* Document Image */}
            <div 
              className="relative bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden"
              style={{ transform: `scale(${zoomLevel})` }}
            >
              {/* Simulated invoice document */}
              <div className="w-64 h-80 p-4 text-xs">
                <div className="border-b border-gray-200 pb-2 mb-4">
                  <div className="font-bold text-lg text-blue-600">ACME CORP</div>
                  <div className="text-gray-600">123 Business St, City, ST 12345</div>
                </div>
                
                <div className="mb-4">
                  <div className="font-semibold mb-1">INVOICE</div>
                  <div className="flex justify-between">
                    <span>Invoice #:</span>
                    <span className={selectedField === 'invoiceNumber' ? 'bg-blue-200' : ''}>
                      INV-2024-001
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Date:</span>
                    <span className={selectedField === 'date' ? 'bg-blue-200' : ''}>
                      March 15, 2024
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Due:</span>
                    <span className={selectedField === 'dueDate' ? 'bg-blue-200' : ''}>
                      April 14, 2024
                    </span>
                  </div>
                </div>
                
                <div className="mb-4">
                  <div className="font-semibold mb-1">Bill To:</div>
                  <div>Your Company Name</div>
                  <div>456 Client Ave</div>
                  <div>City, ST 12345</div>
                </div>
                
                <div className="mb-4">
                  <div className="border-b border-gray-200 pb-1 mb-2">
                    <div className="font-semibold">Description</div>
                  </div>
                  <div className={selectedField === 'description' ? 'bg-blue-200' : ''}>
                    Professional Services - Q1 2024
                  </div>
                </div>
                
                <div className="border-t border-gray-200 pt-2">
                  <div className="flex justify-between font-bold text-lg">
                    <span>Total:</span>
                    <span className={selectedField === 'amount' ? 'bg-blue-200' : ''}>
                      $2,450.00
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Zoom Controls */}
            <div className="absolute bottom-4 right-4 flex space-x-2">
              <button 
                onClick={() => setZoomLevel(Math.max(0.5, zoomLevel - 0.25))}
                className="w-10 h-10 bg-white rounded-full shadow-lg border border-gray-200 flex items-center justify-center"
              >
                <ZoomOut className="w-5 h-5 text-gray-600" />
              </button>
              <button 
                onClick={() => setZoomLevel(Math.min(2, zoomLevel + 0.25))}
                className="w-10 h-10 bg-white rounded-full shadow-lg border border-gray-200 flex items-center justify-center"
              >
                <ZoomIn className="w-5 h-5 text-gray-600" />
              </button>
            </div>
          </div>
        </div>

        {/* Data Fields */}
        <div className="lg:w-3/5 flex-1">
          <div className="p-6 space-y-6">
            
            {/* AI Processing Status */}
            <div className="bg-blue-50 rounded-2xl p-4 border border-blue-100">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                <span className="text-blue-700 font-medium text-sm">
                  AI extracted {Object.values(formData).filter(f => f.confidence >= 85).length} of {Object.keys(formData).length} fields with high confidence
                </span>
              </div>
            </div>

            {/* Form Fields */}
            <div className="space-y-4">
              
              {/* Vendor Name */}
              <div className="space-y-2">
                <label className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
                  Vendor Name
                </label>
                <div 
                  className={`relative ${getConfidenceColor(formData.vendor.confidence)} rounded-xl border transition-all duration-200`}
                  onMouseEnter={() => setSelectedField('vendor')}
                  onMouseLeave={() => setSelectedField(null)}
                >
                  <input
                    type="text"
                    value={formData.vendor.value}
                    onChange={(e) => handleFieldEdit('vendor', e.target.value)}
                    className="w-full p-4 bg-transparent text-black font-semibold text-lg rounded-xl border-none outline-none"
                    placeholder="Vendor name"
                  />
                  <div className={`absolute right-4 top-1/2 transform -translate-y-1/2 w-3 h-3 rounded-full ${getConfidenceIndicator(formData.vendor.confidence, formData.vendor.verified)}`}></div>
                </div>
              </div>

              {/* Invoice Amount */}
              <div className="space-y-2">
                <label className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
                  Amount
                </label>
                <div 
                  className={`relative ${getConfidenceColor(formData.amount.confidence)} rounded-xl border transition-all duration-200`}
                  onMouseEnter={() => setSelectedField('amount')}
                  onMouseLeave={() => setSelectedField(null)}
                >
                  <div className="flex">
                    <div className="flex items-center justify-center px-4 text-gray-600 font-semibold text-lg">$</div>
                    <input
                      type="text"
                      value={formData.amount.value}
                      onChange={(e) => handleFieldEdit('amount', e.target.value)}
                      className="flex-1 p-4 pl-0 bg-transparent text-black font-bold text-xl rounded-xl border-none outline-none"
                      placeholder="0.00"
                    />
                  </div>
                  <div className={`absolute right-4 top-1/2 transform -translate-y-1/2 w-3 h-3 rounded-full ${getConfidenceIndicator(formData.amount.confidence, formData.amount.verified)}`}></div>
                </div>
              </div>

              {/* Two-column layout for invoice details */}
              <div className="grid grid-cols-2 gap-4">
                
                {/* Invoice Number */}
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
                    Invoice #
                  </label>
                  <div 
                    className={`relative ${getConfidenceColor(formData.invoiceNumber.confidence)} rounded-xl border transition-all duration-200`}
                    onMouseEnter={() => setSelectedField('invoiceNumber')}
                    onMouseLeave={() => setSelectedField(null)}
                  >
                    <input
                      type="text"
                      value={formData.invoiceNumber.value}
                      onChange={(e) => handleFieldEdit('invoiceNumber', e.target.value)}
                      className="w-full p-4 bg-transparent text-black font-mono text-sm rounded-xl border-none outline-none"
                      placeholder="Invoice number"
                    />
                    <div className={`absolute right-3 top-1/2 transform -translate-y-1/2 w-2 h-2 rounded-full ${getConfidenceIndicator(formData.invoiceNumber.confidence, formData.invoiceNumber.verified)}`}></div>
                  </div>
                </div>

                {/* Invoice Date */}
                <div className="space-y-2">
                  <label className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
                    Date
                  </label>
                  <div 
                    className={`relative ${getConfidenceColor(formData.date.confidence)} rounded-xl border transition-all duration-200`}
                    onMouseEnter={() => setSelectedField('date')}
                    onMouseLeave={() => setSelectedField(null)}
                  >
                    <input
                      type="text"
                      value={formData.date.value}
                      onChange={(e) => handleFieldEdit('date', e.target.value)}
                      className="w-full p-4 bg-transparent text-black text-sm rounded-xl border-none outline-none"
                      placeholder="Invoice date"
                    />
                    <div className={`absolute right-3 top-1/2 transform -translate-y-1/2 w-2 h-2 rounded-full ${getConfidenceIndicator(formData.date.confidence, formData.date.verified)}`}></div>
                  </div>
                </div>
              </div>

              {/* Due Date */}
              <div className="space-y-2">
                <label className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
                  Due Date
                </label>
                <div 
                  className={`relative ${getConfidenceColor(formData.dueDate.confidence)} rounded-xl border transition-all duration-200`}
                  onMouseEnter={() => setSelectedField('dueDate')}
                  onMouseLeave={() => setSelectedField(null)}
                >
                  <input
                    type="text"
                    value={formData.dueDate.value}
                    onChange={(e) => handleFieldEdit('dueDate', e.target.value)}
                    className="w-full p-4 bg-transparent text-black text-sm rounded-xl border-none outline-none"
                    placeholder="Due date"
                  />
                  <div className={`absolute right-4 top-1/2 transform -translate-y-1/2 w-3 h-3 rounded-full ${getConfidenceIndicator(formData.dueDate.confidence, formData.dueDate.verified)}`}></div>
                </div>
              </div>

              {/* Description */}
              <div className="space-y-2">
                <label className="text-sm font-semibold text-gray-900 uppercase tracking-wide">
                  Description
                </label>
                <div 
                  className={`relative ${getConfidenceColor(formData.description.confidence)} rounded-xl border transition-all duration-200`}
                  onMouseEnter={() => setSelectedField('description')}
                  onMouseLeave={() => setSelectedField(null)}
                >
                  <textarea
                    value={formData.description.value}
                    onChange={(e) => handleFieldEdit('description', e.target.value)}
                    className="w-full p-4 bg-transparent text-black text-sm rounded-xl border-none outline-none resize-none"
                    rows="3"
                    placeholder="Invoice description"
                  />
                  <div className={`absolute right-4 top-4 w-3 h-3 rounded-full ${getConfidenceIndicator(formData.description.confidence, formData.description.verified)}`}></div>
                </div>
              </div>
            </div>

            {/* AI Learning Feedback */}
            {showingLearning && (
              <div className="bg-green-50 rounded-xl p-4 border border-green-200 animate-fadeIn">
                <div className="flex items-center space-x-3">
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  <span className="text-green-700 font-medium">Thanks! I'll remember this for next time.</span>
                </div>
              </div>
            )}

            {/* Confidence Legend */}
            <div className="bg-gray-50 rounded-xl p-4">
              <div className="text-sm font-medium text-gray-900 mb-3">Confidence Levels</div>
              <div className="space-y-2">
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">Verified by you</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">High confidence (90%+)</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-blue-400 rounded-full"></div>
                  <span className="text-sm text-gray-600">Medium confidence (70-89%)</span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 bg-orange-400 rounded-full"></div>
                  <span className="text-sm text-gray-600">Needs review (below 70%)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Action Bar */}
      <div className="sticky bottom-0 bg-white border-t border-gray-200 p-6 pb-12">
        <div className="flex space-x-4">
          <button className="flex-1 bg-gray-100 text-gray-700 font-semibold py-4 rounded-xl transition-all duration-200 active:scale-98">
            Save Draft
          </button>
          
          <button 
            className={`flex-1 font-semibold py-4 rounded-xl transition-all duration-200 active:scale-98 flex items-center justify-center space-x-2 ${
              allFieldsVerified 
                ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/25' 
                : 'bg-blue-100 text-blue-400'
            }`}
            disabled={!allFieldsVerified}
          >
            <Check className="w-5 h-5" />
            <span>Approve Invoice</span>
          </button>
        </div>
        
        {!allFieldsVerified && (
          <div className="text-center mt-3">
            <span className="text-sm text-gray-500">
              Review {Object.values(formData).filter(f => !f.verified).length} remaining fields to approve
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default InvoiceReview;