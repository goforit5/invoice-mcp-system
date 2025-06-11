import React, { useState, useEffect } from 'react';
import { Search, Filter, Plus, ChevronDown, FileText, Clock, CheckCircle2, XCircle, AlertCircle, MoreHorizontal, Archive, Share, Trash2 } from 'lucide-react';

const InvoiceLibrary = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilter, setActiveFilter] = useState('All');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [swipedInvoice, setSwipedInvoice] = useState(null);
  const [swipeDirection, setSwipeDirection] = useState(null);

  const filters = ['All', 'Pending', 'Approved', 'Paid', 'Overdue'];

  const invoices = [
    {
      id: 1,
      vendor: "Acme Corporation",
      amount: "$2,450.00",
      status: "approved",
      date: "Mar 15, 2024",
      dueDate: "Apr 14, 2024",
      invoiceNumber: "INV-2024-001",
      description: "Professional Services - Q1 2024",
      thumbnail: "📄",
      isOverdue: false,
      confidence: 95
    },
    {
      id: 2,
      vendor: "Office Supplies Co",
      amount: "$186.50",
      status: "pending",
      date: "Mar 14, 2024",
      dueDate: "Apr 13, 2024",
      invoiceNumber: "OS-2024-089",
      description: "Office supplies and materials",
      thumbnail: "📋",
      isOverdue: false,
      confidence: 88
    },
    {
      id: 3,
      vendor: "Tech Solutions LLC",
      amount: "$1,200.00",
      status: "processing",
      date: "Mar 13, 2024",
      dueDate: "Apr 12, 2024",
      invoiceNumber: "TS-001-2024",
      description: "Software licensing and support",
      thumbnail: "💻",
      isOverdue: false,
      confidence: 92
    },
    {
      id: 4,
      vendor: "Marketing Agency Pro",
      amount: "$3,750.00",
      status: "paid",
      date: "Feb 28, 2024",
      dueDate: "Mar 30, 2024",
      invoiceNumber: "MAP-2024-Q1",
      description: "Digital marketing campaign",
      thumbnail: "📊",
      isOverdue: false,
      confidence: 98
    },
    {
      id: 5,
      vendor: "Utilities Corp",
      amount: "$345.67",
      status: "overdue",
      date: "Feb 15, 2024",
      dueDate: "Mar 15, 2024",
      invoiceNumber: "UC-FEB-2024",
      description: "Monthly utility charges",
      thumbnail: "⚡",
      isOverdue: true,
      confidence: 85
    }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'approved': return 'text-green-600 bg-green-50';
      case 'pending': return 'text-orange-600 bg-orange-50';
      case 'processing': return 'text-blue-600 bg-blue-50';
      case 'paid': return 'text-gray-600 bg-gray-50';
      case 'overdue': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusDot = (status) => {
    switch (status) {
      case 'approved': return 'bg-green-500';
      case 'pending': return 'bg-orange-500 animate-pulse';
      case 'processing': return 'bg-blue-500 animate-pulse';
      case 'paid': return 'bg-gray-500';
      case 'overdue': return 'bg-red-500 animate-pulse';
      default: return 'bg-gray-500';
    }
  };

  const filteredInvoices = invoices.filter(invoice => {
    const matchesSearch = invoice.vendor.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         invoice.invoiceNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         invoice.description.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesFilter = activeFilter === 'All' || 
                         (activeFilter === 'Overdue' && invoice.isOverdue) ||
                         invoice.status === activeFilter.toLowerCase();
    
    return matchesSearch && matchesFilter;
  });

  const getFilterCount = (filter) => {
    if (filter === 'All') return invoices.length;
    if (filter === 'Overdue') return invoices.filter(inv => inv.isOverdue).length;
    return invoices.filter(inv => inv.status === filter.toLowerCase()).length;
  };

  const handleSwipeStart = (invoiceId, direction) => {
    setSwipedInvoice(invoiceId);
    setSwipeDirection(direction);
  };

  const handleSwipeEnd = () => {
    setSwipedInvoice(null);
    setSwipeDirection(null);
  };

  const groupInvoicesByDate = (invoices) => {
    const today = new Date();
    const thisWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    const thisMonth = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);

    const groups = {
      'Today': [],
      'This Week': [],
      'This Month': [],
      'Earlier': []
    };

    invoices.forEach(invoice => {
      const invoiceDate = new Date(invoice.date);
      if (invoiceDate.toDateString() === today.toDateString()) {
        groups['Today'].push(invoice);
      } else if (invoiceDate > thisWeek) {
        groups['This Week'].push(invoice);
      } else if (invoiceDate > thisMonth) {
        groups['This Month'].push(invoice);
      } else {
        groups['Earlier'].push(invoice);
      }
    });

    return groups;
  };

  const groupedInvoices = groupInvoicesByDate(filteredInvoices);

  return (
    <div className="min-h-screen bg-white">
      
      {/* Header */}
      <div className="bg-white border-b border-gray-100">
        <div className="px-6 py-4 pt-16">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-3xl font-bold text-black">Library</h1>
            <button className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center shadow-lg shadow-blue-500/25">
              <Plus className="w-5 h-5 text-white" />
            </button>
          </div>

          {/* Search Bar */}
          <div className="relative mb-4">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-4 bg-gray-50 border-none rounded-2xl text-black placeholder-gray-500 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all duration-200"
              placeholder="Search invoices, vendors, amounts..."
            />
          </div>

          {/* Filter Tabs */}
          <div className="flex space-x-2 overflow-x-auto pb-2">
            {filters.map((filter) => (
              <button
                key={filter}
                onClick={() => setActiveFilter(filter)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-full font-medium text-sm whitespace-nowrap transition-all duration-200 ${
                  activeFilter === filter
                    ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/25'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <span>{filter}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  activeFilter === filter
                    ? 'bg-white/20 text-white'
                    : 'bg-gray-200 text-gray-500'
                }`}>
                  {getFilterCount(filter)}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Invoice List */}
      <div className="pb-32">
        {Object.entries(groupedInvoices).map(([groupName, groupInvoices]) => {
          if (groupInvoices.length === 0) return null;
          
          return (
            <div key={groupName} className="px-6 py-4">
              <h2 className="text-lg font-bold text-black mb-4">{groupName}</h2>
              
              <div className="space-y-3">
                {groupInvoices.map((invoice) => (
                  <div
                    key={invoice.id}
                    className={`relative bg-white rounded-2xl border border-gray-100 overflow-hidden transition-all duration-200 ${
                      swipedInvoice === invoice.id ? 'transform scale-98' : 'hover:shadow-lg hover:border-gray-200'
                    }`}
                  >
                    
                    {/* Swipe Actions Background */}
                    {swipedInvoice === invoice.id && swipeDirection === 'left' && (
                      <div className="absolute inset-0 bg-green-500 flex items-center justify-start pl-6">
                        <CheckCircle2 className="w-6 h-6 text-white" />
                      </div>
                    )}
                    
                    {swipedInvoice === invoice.id && swipeDirection === 'right' && (
                      <div className="absolute inset-0 bg-gray-500 flex items-center justify-end pr-6">
                        <MoreHorizontal className="w-6 h-6 text-white" />
                      </div>
                    )}

                    {/* Invoice Card Content */}
                    <div className="p-4">
                      <div className="flex items-center justify-between">
                        
                        {/* Left Side - Vendor Info */}
                        <div className="flex items-center space-x-4 flex-1">
                          
                          {/* Status Indicator */}
                          <div className={`w-1 h-12 rounded-full ${
                            invoice.status === 'approved' ? 'bg-green-500' :
                            invoice.status === 'pending' ? 'bg-orange-500' :
                            invoice.status === 'processing' ? 'bg-blue-500' :
                            invoice.status === 'paid' ? 'bg-gray-500' :
                            'bg-red-500'
                          }`}></div>
                          
                          {/* Vendor Details */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center space-x-2 mb-1">
                              <h3 className="font-semibold text-black truncate">{invoice.vendor}</h3>
                              <div className={`w-2 h-2 rounded-full ${getStatusDot(invoice.status)}`}></div>
                            </div>
                            
                            <div className="flex items-center space-x-3 text-sm text-gray-500">
                              <span>{invoice.invoiceNumber}</span>
                              <span>•</span>
                              <span>{invoice.date}</span>
                              {invoice.isOverdue && (
                                <>
                                  <span>•</span>
                                  <span className="text-red-500 font-medium">Overdue</span>
                                </>
                              )}
                            </div>
                            
                            <p className="text-sm text-gray-600 mt-1 truncate">{invoice.description}</p>
                          </div>
                        </div>

                        {/* Right Side - Amount & Status */}
                        <div className="flex flex-col items-end space-y-2">
                          <div className="font-bold text-lg text-black">{invoice.amount}</div>
                          
                          <div className={`px-3 py-1 rounded-full text-xs font-medium capitalize ${getStatusColor(invoice.status)}`}>
                            {invoice.status}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Tap Area for Navigation */}
                    <button 
                      className="absolute inset-0 w-full h-full"
                      onClick={() => setSelectedInvoice(invoice)}
                    />
                  </div>
                ))}
              </div>
            </div>
          );
        })}

        {/* Empty State */}
        {filteredInvoices.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 px-6">
            <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mb-6">
              <FileText className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-black mb-2">
              {searchQuery ? 'No matching invoices' : 'No invoices yet'}
            </h3>
            <p className="text-gray-500 text-center mb-6">
              {searchQuery 
                ? `No invoices match "${searchQuery}". Try a different search term.`
                : 'Start by processing your first invoice with the camera.'
              }
            </p>
            <button className="bg-blue-500 text-white px-6 py-3 rounded-xl font-semibold shadow-lg shadow-blue-500/25">
              {searchQuery ? 'Clear Search' : 'Process Invoice'}
            </button>
          </div>
        )}
      </div>

      {/* Quick Summary Bar */}
      <div className="fixed bottom-20 left-6 right-6 bg-white/95 backdrop-blur-xl rounded-2xl border border-gray-200 p-4 shadow-xl">
        <div className="flex items-center justify-between">
          <div className="text-sm">
            <span className="text-gray-600">Total: </span>
            <span className="font-bold text-black">
              ${invoices.reduce((sum, inv) => sum + parseFloat(inv.amount.replace('$', '').replace(',', '')), 0).toLocaleString()}
            </span>
          </div>
          
          <div className="flex items-center space-x-4 text-sm">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
              <span className="text-gray-600">{getFilterCount('Pending')} pending</span>
            </div>
            
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-red-500 rounded-full"></div>
              <span className="text-gray-600">{getFilterCount('Overdue')} overdue</span>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Tab Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-xl border-t border-gray-200">
        <div className="flex items-center justify-around py-2 pb-8">
          <div className="flex flex-col items-center py-1">
            <div className="w-7 h-7 rounded-full border-2 border-gray-400 flex items-center justify-center mb-1">
              <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
            </div>
            <span className="text-xs text-gray-400">Home</span>
          </div>
          
          <div className="flex flex-col items-center py-1">
            <div className="w-7 h-7 text-gray-400 mb-1">📷</div>
            <span className="text-xs text-gray-400">Scan</span>
          </div>
          
          <div className="flex flex-col items-center py-1">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center mb-1">
              <FileText className="w-4 h-4 text-white" />
            </div>
            <span className="text-xs text-blue-500 font-medium">Library</span>
          </div>
          
          <div className="flex flex-col items-center py-1">
            <div className="w-7 h-7 text-gray-400 mb-1">✓</div>
            <span className="text-xs text-gray-400">Review</span>
          </div>
          
          <div className="flex flex-col items-center py-1">
            <div className="w-7 h-7 rounded-full border-2 border-gray-400 flex items-center justify-center mb-1">
              <div className="w-3 h-3 bg-gray-400 rounded-full"></div>
            </div>
            <span className="text-xs text-gray-400">Settings</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InvoiceLibrary;