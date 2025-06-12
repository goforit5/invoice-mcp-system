import React, { useState, useEffect } from 'react'

const CRMDashboard = ({ onBack, onViewRecord, onViewWorkflow }) => {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [dashboardData, setDashboardData] = useState(null)
  const [contacts, setContacts] = useState([])
  const [companies, setCompanies] = useState([])
  const [communications, setCommunications] = useState([])
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      
      // Load dashboard summary
      const dashboardResponse = await fetch('/api/crm/dashboard')
      const dashboard = await dashboardResponse.json()
      setDashboardData(dashboard)

      // Load recent data for each tab
      const [contactsRes, companiesRes, communicationsRes, tasksRes] = await Promise.all([
        fetch('/api/crm/contacts?limit=10'),
        fetch('/api/crm/companies?limit=10'),
        fetch('/api/crm/communications?limit=20'),
        fetch('/api/crm/tasks?limit=15')
      ])

      setContacts(await contactsRes.json())
      setCompanies(await companiesRes.json())
      setCommunications(await communicationsRes.json())
      setTasks(await tasksRes.json())
    } catch (error) {
      console.error('Failed to load CRM data:', error)
    } finally {
      setLoading(false)
    }
  }

  const searchContacts = async (query) => {
    if (!query.trim()) {
      loadDashboardData()
      return
    }
    
    try {
      const response = await fetch(`/api/crm/search/contacts?q=${encodeURIComponent(query)}`)
      const results = await response.json()
      setContacts(results)
    } catch (error) {
      console.error('Search failed:', error)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'No date'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  }

  const formatDateTime = (dateString) => {
    if (!dateString) return 'No date'
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'urgent': return 'bg-red-100 text-red-800'
      case 'high': return 'bg-orange-100 text-orange-800'
      case 'normal': return 'bg-blue-100 text-blue-800'
      case 'low': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'urgent': return 'bg-red-100 text-red-800'
      case 'high': return 'bg-orange-100 text-orange-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-purple-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">CRM Dashboard</h2>
          <p className="text-gray-600 mt-2">Manage contacts, communications, and tasks</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={onViewWorkflow}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            🤖 View Workflows
          </button>
          <button
            onClick={onBack}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            ← Back to Processor
          </button>
        </div>
      </div>

      {/* Dashboard Overview */}
      {dashboardData && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 System Overview</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{dashboardData.contacts || 0}</div>
              <div className="text-sm text-gray-600">Active Contacts</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{dashboardData.companies || 0}</div>
              <div className="text-sm text-gray-600">Companies</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{dashboardData.communications || 0}</div>
              <div className="text-sm text-gray-600">Communications</div>
            </div>
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">{dashboardData.urgentTasks || 0}</div>
              <div className="text-sm text-gray-600">Urgent Tasks</div>
            </div>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { id: 'contacts', label: '👥 Contacts', count: contacts.length },
              { id: 'companies', label: '🏢 Companies', count: companies.length },
              { id: 'communications', label: '💬 Communications', count: communications.length },
              { id: 'tasks', label: '✅ Tasks', count: tasks.length }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label} ({tab.count})
              </button>
            ))}
          </nav>
        </div>

        {/* Search Bar */}
        <div className="p-6 border-b border-gray-200">
          <div className="relative">
            <input
              type="text"
              placeholder={`Search ${activeTab}...`}
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value)
                if (activeTab === 'contacts') {
                  searchContacts(e.target.value)
                }
              }}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {/* Contacts Tab */}
          {activeTab === 'contacts' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="text-lg font-medium text-gray-900">Recent Contacts</h4>
                <button className="text-sm text-purple-600 hover:text-purple-700">
                  + Add Contact
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Contact
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Company
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Created
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {contacts.slice(0, 10).map((contact) => (
                      <tr key={contact.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">
                              {contact.first_name} {contact.last_name}
                            </div>
                            <div className="text-sm text-gray-500">{contact.email}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {contact.company_name || 'No company'}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            contact.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {contact.status || 'active'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {formatDate(contact.created_at)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Companies Tab */}
          {activeTab === 'companies' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="text-lg font-medium text-gray-900">Companies</h4>
                <button className="text-sm text-purple-600 hover:text-purple-700">
                  + Add Company
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {companies.slice(0, 9).map((company) => (
                  <div key={company.id} className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors">
                    <div className="flex items-start justify-between">
                      <div>
                        <h5 className="font-medium text-gray-900">{company.name}</h5>
                        <p className="text-sm text-gray-600 mt-1">{company.industry || 'No industry'}</p>
                        {company.phone && (
                          <p className="text-sm text-gray-500 mt-1">📞 {company.phone}</p>
                        )}
                      </div>
                      <span className="text-xs text-gray-500">
                        {formatDate(company.created_at)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Communications Tab */}
          {activeTab === 'communications' && (
            <div className="space-y-4">
              <h4 className="text-lg font-medium text-gray-900">Recent Communications</h4>
              <div className="space-y-3">
                {communications.slice(0, 10).map((comm) => (
                  <div key={comm.id} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-gray-900">
                            {comm.sender_display_name || comm.sender_identifier}
                          </span>
                          <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded">
                            {comm.platform}
                          </span>
                          {comm.urgency_level && (
                            <span className={`text-xs px-2 py-1 rounded ${getUrgencyColor(comm.urgency_level)}`}>
                              {comm.urgency_level}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-gray-900 mt-1 font-medium">{comm.subject_line}</p>
                        <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                          {comm.message_content_text?.substring(0, 200)}...
                        </p>
                      </div>
                      <div className="text-xs text-gray-500">
                        {formatDateTime(comm.communication_timestamp)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tasks Tab */}
          {activeTab === 'tasks' && (
            <div className="space-y-4">
              <h4 className="text-lg font-medium text-gray-900">Active Tasks</h4>
              <div className="space-y-3">
                {tasks.slice(0, 10).map((task) => (
                  <div key={task.id} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          <h5 className="text-sm font-medium text-gray-900">{task.title}</h5>
                          <span className={`text-xs px-2 py-1 rounded ${getPriorityColor(task.priority)}`}>
                            {task.priority}
                          </span>
                          {task.completed && (
                            <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded">
                              ✓ Completed
                            </span>
                          )}
                        </div>
                        {task.description && (
                          <p className="text-sm text-gray-600 mt-1">{task.description}</p>
                        )}
                        {task.contact_name && (
                          <p className="text-xs text-gray-500 mt-1">👤 {task.contact_name}</p>
                        )}
                      </div>
                      <div className="text-xs text-gray-500">
                        {task.due_date ? `Due: ${formatDate(task.due_date)}` : 'No due date'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default CRMDashboard