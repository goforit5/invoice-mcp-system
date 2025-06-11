import React, { useState, useEffect } from 'react';
import { X, Camera, Zap, ZapOff, RotateCcw, Check, FileText, Image } from 'lucide-react';

const InvoiceCapture = () => {
  const [captureState, setCaptureState] = useState('searching'); // searching, detected, captured, processing
  const [flashOn, setFlashOn] = useState(false);
  const [documentDetected, setDocumentDetected] = useState(false);
  const [countdown, setCountdown] = useState(null);
  const [confidence, setConfidence] = useState(0);

  // Simulate document detection
  useEffect(() => {
    const detectionTimer = setTimeout(() => {
      setDocumentDetected(true);
      setCaptureState('detected');
      setConfidence(95);
      
      // Auto-capture countdown
      const countdownTimer = setTimeout(() => {
        if (captureState === 'detected') {
          handleCapture();
        }
      }, 2000);
      
      return () => clearTimeout(countdownTimer);
    }, 3000);
    
    return () => clearTimeout(detectionTimer);
  }, []);

  // Countdown for auto-capture
  useEffect(() => {
    if (captureState === 'detected') {
      let count = 2;
      setCountdown(count);
      
      const countdownInterval = setInterval(() => {
        count -= 1;
        setCountdown(count);
        
        if (count === 0) {
          clearInterval(countdownInterval);
          setCountdown(null);
        }
      }, 1000);
      
      return () => clearInterval(countdownInterval);
    }
  }, [captureState]);

  const handleCapture = () => {
    setCaptureState('captured');
    setCountdown(null);
    
    // Brief capture flash effect
    setTimeout(() => {
      setCaptureState('processing');
    }, 500);
  };

  const handleRetake = () => {
    setCaptureState('searching');
    setDocumentDetected(false);
    setConfidence(0);
    setCountdown(null);
  };

  const handleManualEntry = () => {
    // Navigate to manual entry flow
    console.log('Manual entry selected');
  };

  return (
    <div className="min-h-screen bg-black relative overflow-hidden">
      
      {/* Camera Viewfinder Background */}
      <div className="absolute inset-0">
        <div className="w-full h-full bg-gradient-to-br from-gray-800 via-gray-700 to-gray-900 opacity-90"></div>
        {/* Simulated camera noise/grain */}
        <div className="absolute inset-0 opacity-10" 
             style={{
               backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Ccircle cx='7' cy='7' r='1'/%3E%3Ccircle cx='47' cy='13' r='1'/%3E%3Ccircle cx='27' cy='23' r='1'/%3E%3Ccircle cx='37' cy='37' r='1'/%3E%3Ccircle cx='17' cy='47' r='1'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
             }}>
        </div>
      </div>

      {/* Top Controls */}
      <div className="relative z-10 flex items-center justify-between p-6 pt-16">
        <button className="w-10 h-10 bg-black/30 backdrop-blur-xl rounded-full flex items-center justify-center border border-white/20">
          <X className="w-5 h-5 text-white" />
        </button>
        
        <div className="flex items-center space-x-4">
          <button 
            onClick={() => setFlashOn(!flashOn)}
            className="w-10 h-10 bg-black/30 backdrop-blur-xl rounded-full flex items-center justify-center border border-white/20"
          >
            {flashOn ? <Zap className="w-5 h-5 text-yellow-400" /> : <ZapOff className="w-5 h-5 text-white" />}
          </button>
        </div>
      </div>

      {/* Document Detection Overlay */}
      {captureState === 'searching' && (
        <div className="absolute inset-0 flex items-center justify-center z-20">
          <div className="w-80 h-60 border-2 border-dashed border-white/40 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <div className="w-12 h-12 border-2 border-white/60 border-t-white rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-white/80 text-lg font-medium">Looking for invoice...</p>
              <p className="text-white/60 text-sm mt-2">Position document in frame</p>
            </div>
          </div>
        </div>
      )}

      {/* Document Detected Overlay */}
      {captureState === 'detected' && (
        <div className="absolute inset-0 flex items-center justify-center z-20">
          <div className="relative">
            {/* Animated border */}
            <div className="w-80 h-60 border-3 border-blue-500 rounded-lg relative overflow-hidden">
              <div className="absolute inset-0 border-3 border-blue-400 rounded-lg animate-pulse"></div>
              
              {/* Corner indicators */}
              <div className="absolute top-2 left-2 w-4 h-4 border-l-3 border-t-3 border-blue-500"></div>
              <div className="absolute top-2 right-2 w-4 h-4 border-r-3 border-t-3 border-blue-500"></div>
              <div className="absolute bottom-2 left-2 w-4 h-4 border-l-3 border-b-3 border-blue-500"></div>
              <div className="absolute bottom-2 right-2 w-4 h-4 border-r-3 border-b-3 border-blue-500"></div>
            </div>
            
            {/* Success message */}
            <div className="absolute -bottom-16 left-1/2 transform -translate-x-1/2 text-center">
              <div className="flex items-center justify-center space-x-2 bg-black/60 backdrop-blur-xl rounded-full px-4 py-2 border border-white/20">
                <Check className="w-4 h-4 text-green-400" />
                <span className="text-white font-medium">Invoice detected</span>
                {countdown && (
                  <span className="text-blue-400 font-bold">{countdown}</span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Capture Flash Effect */}
      {captureState === 'captured' && (
        <div className="absolute inset-0 bg-white z-30 animate-pulse"></div>
      )}

      {/* Processing State */}
      {captureState === 'processing' && (
        <div className="absolute inset-0 bg-black/90 backdrop-blur-sm z-30 flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 border-3 border-blue-500 border-t-blue-300 rounded-full animate-spin mx-auto mb-6"></div>
            <h3 className="text-white text-xl font-semibold mb-2">Processing invoice...</h3>
            <p className="text-white/70">Extracting data with AI</p>
            
            {/* Processing steps */}
            <div className="mt-8 space-y-3">
              <div className="flex items-center justify-center space-x-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                <span className="text-white/80 text-sm">Scanning document</span>
              </div>
              <div className="flex items-center justify-center space-x-3">
                <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" style={{animationDelay: '0.5s'}}></div>
                <span className="text-white/80 text-sm">Identifying fields</span>
              </div>
              <div className="flex items-center justify-center space-x-3">
                <div className="w-2 h-2 bg-blue-300 rounded-full animate-pulse" style={{animationDelay: '1s'}}></div>
                <span className="text-white/80 text-sm">Extracting data</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Guidance Text */}
      {captureState === 'searching' && (
        <div className="absolute bottom-40 left-0 right-0 z-20">
          <div className="text-center px-6">
            <p className="text-white/90 text-lg font-medium mb-2">Align invoice in frame</p>
            <p className="text-white/70 text-sm">Ensure good lighting and hold steady</p>
          </div>
        </div>
      )}

      {/* Bottom Controls */}
      <div className="absolute bottom-0 left-0 right-0 z-20 pb-12">
        <div className="flex items-center justify-center space-x-12 px-6">
          
          {/* Photo Library */}
          <button className="w-12 h-12 bg-black/30 backdrop-blur-xl rounded-lg flex items-center justify-center border border-white/20">
            <Image className="w-6 h-6 text-white" />
          </button>
          
          {/* Capture Button */}
          <button 
            onClick={handleCapture}
            disabled={captureState === 'searching'}
            className={`w-20 h-20 rounded-full border-4 flex items-center justify-center transition-all duration-200 ${
              captureState === 'detected' 
                ? 'border-blue-500 bg-blue-500/20 backdrop-blur-xl' 
                : 'border-white/60 bg-white/10 backdrop-blur-xl'
            } ${captureState === 'searching' ? 'opacity-50' : 'active:scale-95'}`}
          >
            <div className={`w-16 h-16 rounded-full transition-all duration-200 ${
              captureState === 'detected' ? 'bg-blue-500' : 'bg-white/80'
            }`}></div>
          </button>
          
          {/* Retake/Manual Entry */}
          <button 
            onClick={captureState === 'detected' ? handleRetake : handleManualEntry}
            className="w-12 h-12 bg-black/30 backdrop-blur-xl rounded-lg flex items-center justify-center border border-white/20"
          >
            {captureState === 'detected' ? (
              <RotateCcw className="w-6 h-6 text-white" />
            ) : (
              <FileText className="w-6 h-6 text-white" />
            )}
          </button>
        </div>
        
        {/* Manual Entry Option */}
        {captureState === 'searching' && (
          <div className="text-center mt-6">
            <button 
              onClick={handleManualEntry}
              className="text-white/80 text-sm font-medium hover:text-white transition-colors"
            >
              Can't scan? Enter manually
            </button>
          </div>
        )}
      </div>

      {/* Confidence Indicator (when detected) */}
      {captureState === 'detected' && confidence > 0 && (
        <div className="absolute top-32 right-6 z-20">
          <div className="bg-black/60 backdrop-blur-xl rounded-full px-3 py-1 border border-white/20">
            <span className="text-white text-xs font-medium">{confidence}% confident</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default InvoiceCapture;