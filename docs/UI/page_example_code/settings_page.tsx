import React, { useState } from 'react';
import { ChevronLeft, ChevronRight, User, Brain, Bell, Shield, Download, HelpCircle, Mail, Star, Trash2, Eye, Moon, Sun, Zap, Clock, FileText } from 'lucide-react';

const Settings = () => {
  const [aiLearning, setAiLearning] = useState(true);
  const [notifications, setNotifications] = useState(true);
  const [autoApproval, setAutoApproval] = useState(false);
  const [confidenceThreshold, setConfidenceThreshold] = useState(85);
  const [darkMode, setDarkMode] = useState(false);
  const [hapticFeedback, setHapticFeedback] = useState(true);

  const SettingsSection = ({ title, children }) => (
    <div className="bg-white rounded-2xl border border-gray-100 overflow-hidden mb-6">
      <div className="px-6 py-4 border-b border-gray-50">
        <h2 className="font-semibold text-black text-lg">{title}</h2>
      </div>
      {children}
    </div>
  );

  const SettingsRow = ({ icon: Icon, title, subtitle, action, showChevron = false, isDestructive = false }) => (
    <div className={`flex items-center justify-between px-6 py-4 border-b border-gray-50 last:border-b-0 ${
      isDestructive ? 'hover:bg-red-25' : 'hover:bg-gray-25'
    } transition-colors cursor-pointer`}>
      <div className="flex items-center space-x-4 flex-1">
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
          isDestructive ? 'bg-red-100' : 'bg-gray-100'
        }`}>
          <Icon className={`w-4 h-4 ${isDestructive ? 'text-red-600' : 'text-gray-600'}`} />
        </div>
        <div className="flex-1">
          <div className={`font-medium ${isDestructive ? 'text-red-600' : 'text-black'}`}>
            {title}
          </div>
          {subtitle && (
            <div className="text-sm text-gray-500 mt-0.5">{subtitle}</div>
          )}
        </div>
      </div>
      <div className="flex items-center space-x-3">
        {action}
        {showChevron && (
          <ChevronRight className="w-5 h-5 text-gray-400" />
        )}
      </div>
    </div>
  );

  const Toggle = ({ enabled, onChange }) => (
    <button
      onClick={() => onChange(!enabled)}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
        enabled ? 'bg-blue-500' : 'bg-gray-200'
      }`}
    >
      <span
        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
          enabled ? 'translate-x-6' : 'translate-x-1'
        }`}
      />
    </button>
  );

  const ConfidenceSlider = () => (
    <div className="w-32">
      <div className="flex items-center justify-between text-xs text-gray-500 mb-2">
        <span>50%</span>
        <span className="font-medium text-black">{confidenceThreshold}%</span>
        <span>95%</span>
      </div>
      <div className="relative">
        <input
          type="range"
          min="50"
          max="95"
          value={confidenceThreshold}
          onChange={(e) => setConfidenceThreshold(parseInt(e.target.value))}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          style={{
            background: `linear-gradient(to right, #3B82F6 0%, #3B82F6 ${((confidenceThreshold - 50) / 45) * 100}%, #E5E7EB ${((confidenceThreshold - 50) / 45) * 100}%, #E5E7EB 100%)`
          }}
        />
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      
      {/* Header */}
      <div className="bg-white border-b border-gray-100">
        <div className="px-6 py-4 pt-16">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-black">Settings</h1>
            <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-gray-600" />
            </div>
          </div>
        </div>
      </div>

      <div className="px-6 py-6 pb-32">
        
        {/* Account Section */}
        <SettingsSection title="Account">
          <SettingsRow
            icon={User}
            title="Profile"
            subtitle="john.doe@company.com"
            showChevron={true}
          />
          <SettingsRow
            icon={FileText}
            title="Usage Statistics"
            subtitle="247 invoices processed this month"
            action={
              <div className="text-right">
                <div className="text-sm font-medium text-green-600">+40% efficiency</div>
                <div className="text-xs text-gray-500">vs last month</div>
              </div>
            }
            showChevron={true}
          />
          <SettingsRow
            icon={Star}
            title="Subscription"
            subtitle="Pro Plan - Unlimited processing"
            action={
              <div className="px-3 py-1 bg-blue-100 rounded-full">
                <span className="text-xs font-medium text-blue-700">Active</span>
              </div>
            }
            showChevron={true}
          />
        </SettingsSection>

        {/* AI Intelligence Section */}
        <SettingsSection title="AI Intelligence">
          <SettingsRow
            icon={Brain}
            title="Learn from corrections"
            subtitle="Improve accuracy from your feedback"
            action={<Toggle enabled={aiLearning} onChange={setAiLearning} />}
          />
          <SettingsRow
            icon={Zap}
            title="Auto-approval threshold"
            subtitle="Automatically approve high-confidence invoices"
            action={<ConfidenceSlider />}
          />
          <SettingsRow
            icon={Clock}
            title="Processing speed"
            subtitle="Balance between speed and accuracy"
            action={
              <div className="text-sm text-blue-600 font-medium">Balanced</div>
            }
            showChevron={true}
          />
          <SettingsRow
            icon={Eye}
            title="Confidence display"
            subtitle="Show AI confidence levels on fields"
            action={<Toggle enabled={true} onChange={() => {}} />}
          />
        </SettingsSection>

        {/* App Behavior Section */}
        <SettingsSection title="App Behavior">
          <SettingsRow
            icon={Bell}
            title="Notifications"
            subtitle="Invoice processing updates and reminders"
            action={<Toggle enabled={notifications} onChange={setNotifications} />}
          />
          <SettingsRow
            icon={darkMode ? Moon : Sun}
            title="Appearance"
            subtitle={darkMode ? "Dark mode" : "Light mode"}
            action={<Toggle enabled={darkMode} onChange={setDarkMode} />}
          />
          <SettingsRow
            icon={Zap}
            title="Haptic feedback"
            subtitle="Vibration for button presses and actions"
            action={<Toggle enabled={hapticFeedback} onChange={setHapticFeedback} />}
          />
        </SettingsSection>

        {/* Data & Privacy Section */}
        <SettingsSection title="Data & Privacy">
          <SettingsRow
            icon={Shield}
            title="Privacy settings"
            subtitle="Control how your data is used"
            showChevron={true}
          />
          <SettingsRow
            icon={Download}
            title="Export data"
            subtitle="Download your invoices and processing history"
            action={
              <div className="text-sm text-blue-600 font-medium">Export</div>
            }
          />
          <SettingsRow
            icon={FileText}
            title="Data retention"
            subtitle="Invoices kept for 7 years, as required by law"
            showChevron={true}
          />
        </SettingsSection>

        {/* Help & Support Section */}
        <SettingsSection title="Help & Support">
          <SettingsRow
            icon={HelpCircle}
            title="Help center"
            subtitle="Guides, tutorials, and FAQ"
            showChevron={true}
          />
          <SettingsRow
            icon={Mail}
            title="Contact support"
            subtitle="Get help from our team"
            showChevron={true}
          />
          <SettingsRow
            icon={Star}
            title="Rate the app"
            subtitle="Share your experience on the App Store"
            showChevron={true}
          />
        </SettingsSection>

        {/* Advanced Section */}
        <SettingsSection title="Advanced">
          <SettingsRow
            icon={Download}
            title="Reset AI learning"
            subtitle="Clear all learned preferences and start fresh"
            isDestructive={true}
          />
          <SettingsRow
            icon={Trash2}
            title="Delete all data"
            subtitle="Permanently remove all invoices and settings"
            isDestructive={true}
          />
        </SettingsSection>

        {/* App Info */}
        <div className="text-center pt-8 pb-4">
          <div className="text-sm text-gray-500 mb-2">Invoice AI Pro</div>
          <div className="text-xs text-gray-400">Version 2.1.0 • Build 1247</div>
          <div className="text-xs text-gray-400 mt-1">© 2024 Your Company</div>
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
            <FileText className="w-7 h-7 text-gray-400 mb-1" />
            <span className="text-xs text-gray-400">Library</span>
          </div>
          
          <div className="flex flex-col items-center py-1">
            <div className="w-7 h-7 text-gray-400 mb-1">✓</div>
            <span className="text-xs text-gray-400">Review</span>
          </div>
          
          <div className="flex flex-col items-center py-1">
            <div className="w-8 h-8 bg-gray-800 rounded-full flex items-center justify-center mb-1">
              <div className="w-4 h-4 bg-white rounded-full"></div>
            </div>
            <span className="text-xs text-black font-medium">Settings</span>
          </div>
        </div>
      </div>

      {/* Custom slider styles */}
      <style jsx>{`
        .slider::-webkit-slider-thumb {
          appearance: none;
          height: 16px;
          width: 16px;
          border-radius: 50%;
          background: #3B82F6;
          cursor: pointer;
          border: 2px solid white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .slider::-moz-range-thumb {
          height: 16px;
          width: 16px;
          border-radius: 50%;
          background: #3B82F6;
          cursor: pointer;
          border: 2px solid white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
      `}</style>
    </div>
  );
};

export default Settings;