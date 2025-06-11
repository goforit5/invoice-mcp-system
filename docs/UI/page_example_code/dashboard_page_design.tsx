import React, { useState, useEffect } from 'react';
import { Plus, Camera, FileText, TrendingUp, Clock, CheckCircle, AlertCircle, ChevronRight, Zap } from 'lucide-react';

const Dashboard = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [aiProcessing, setAiProcessing] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Simulate AI processing pulse
  useEffect(() => {
    const processingTimer = setInterval(() => {
      setAiProcessing(prev => !prev);
    }, 2000);
    return () => clearInterval(processingTimer);
  }, []);

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getGreeting = () => {
    const hour = currentTime.getHours();
    if (hour < 12) return "Good morning";
    if (hour < 17) return "Good afternoon";
    return "Good evening";
  };

  return (
    <div className="min-h-screen bg-white">
      {/* App Content Starts Here */}
      <div className="pt-12"></div>

      {/* Minimal Header - Pure Apple Style */}
      <div className="px-6 pt-8 pb-12">
        <div className="flex items-end justify-between">
          <div>
            <h1 className="text-4xl font-bold text-black tracking-tight leading-none">{getGreeting()}</h1>
            <div className="flex items-center mt-2">
              <div className={`w-2 h-2 rounded-full mr-3 transition-all duration-1000 ${
                aiProcessing ? 'bg-blue-500 shadow-lg shadow-blue-500/30' : 'bg-blue-400'
              }`}></div>
              <span className="text-gray-600 text-lg font-light">Ready to process</span>
            </div>
          </div>
        </div>
      </div>

      {/* Primary Action - Hero Button */}
      <div className="px-6 mb-12">
        <button className="w-full bg-blue-500 text-white font-semibold py-5 rounded-2xl transition-all duration-200 transform active:scale-98 shadow-lg shadow-blue-500/25">
          <div className="flex items-center justify-center space-x-3">
            <Camera className="w-6 h-6" />
            <span className="text-lg">Process Invoice</span>
          </div>
        </button>
      </div>

      {/* Stats - Minimal Cards */}
      <div className="px-6 mb-12">
        <div className="flex space-x-4">
          <div className="flex-1 bg-gray-50 rounded-2xl p-6">
            <div className="text-3xl font-bold text-black mb-1">3</div>
            <div className="text-gray-500 text-sm font-medium tracking-wide uppercase">Pending</div>
            <div className="w-1 h-1 bg-orange-500 rounded-full mt-3"></div>
          </div>
          
          <div className="flex-1 bg-gray-50 rounded-2xl p-6">
            <div className="text-3xl font-bold text-black mb-1">$12.4K</div>
            <div className="text-gray-500 text-sm font-medium tracking-wide uppercase">This Month</div>
            <TrendingUp className="w-4 h-4 text-green-500 mt-3" />
          </div>
        </div>
      </div>

      {/* AI Insight - Distinctive but Minimal */}
      <div className="px-6 mb-12">
        <div className="bg-blue-50 rounded-2xl p-6 border border-blue-100">
          <div className="flex items-start space-x-4">
            <div className="bg-blue-500 rounded-full p-2">
              <Zap className="w-4 h-4 text-white" />
            </div>
            <div className="flex-1">
              <div className="text-black font-semibold mb-2">AI Insight</div>
              <div className="text-gray-700 mb-4 leading-relaxed">
                You're processing invoices 40% faster this month. 3 invoices from Acme Corp are ready for bulk approval.
              </div>
              <button className="text-blue-500 font-semibold">
                Review now
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity - Clean List */}
      <div className="px-6 mb-32">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-black">Recent</h2>
          <button className="text-blue-500 font-semibold">View All</button>
        </div>
        
        <div className="space-y-4">
          {[
            { vendor: "Acme Corporation", amount: "$2,450.00", status: "approved", time: "2m" },
            { vendor: "Office Supplies Co", amount: "$186.50", status: "pending", time: "1h" },
            { vendor: "Tech Solutions LLC", amount: "$1,200.00", status: "processing", time: "3h" }
          ].map((invoice, index) => (
            <div key={index} className="flex items-center justify-between py-4 border-b border-gray-100 last:border-b-0">
              <div className="flex items-center space-x-4">
                <div className={`w-3 h-3 rounded-full ${
                  invoice.status === 'approved' ? 'bg-green-500' :
                  invoice.status === 'pending' ? 'bg-orange-500' :
                  'bg-blue-500'
                } ${invoice.status === 'processing' ? 'animate-pulse' : ''}`}></div>
                <div>
                  <div className="font-semibold text-black">{invoice.vendor}</div>
                  <div className="text-gray-500 text-sm">{invoice.time} ago</div>
                </div>
              </div>
              <div className="text-right">
                <div className="font-bold text-black">{invoice.amount}</div>
                <div className={`text-sm capitalize ${
                  invoice.status === 'approved' ? 'text-green-600' :
                  invoice.status === 'pending' ? 'text-orange-600' :
                  'text-blue-600'
                }`}>
                  {invoice.status}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* True iOS Tab Bar */}
      <div className="fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-xl border-t border-gray-200">
        <div className="flex items-center justify-around py-2 pb-8">
          <div className="flex flex-col items-center py-1">
            <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center mb-1">
              <div className="w-4 h-4 bg-white rounded-full"></div>
            </div>
            <span className="text-xs text-blue-500 font-medium">Home</span>
          </div>
          
          <div className="flex flex-col items-center py-1">
            <Camera className="w-7 h-7 text-gray-400 mb-1" />
            <span className="text-xs text-gray-400">Scan</span>
          </div>
          
          <div className="flex flex-col items-center py-1">
            <FileText className="w-7 h-7 text-gray-400 mb-1" />
            <span className="text-xs text-gray-400">Library</span>
          </div>
          
          <div className="flex flex-col items-center py-1 relative">
            <div className="relative">
              <div className="w-2 h-2 bg-red-500 rounded-full absolute -top-0.5 -right-0.5 z-10"></div>
              <CheckCircle className="w-7 h-7 text-gray-400 mb-1" />
            </div>
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

export default Dashboard;