'use client'

import { useState, useRef, useEffect } from 'react'
import axios from 'axios'

interface LogEntry {
  id: number
  timestamp: string
  type: 'info' | 'error' | 'success' | 'request' | 'response'
  message: string
  data?: any
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string>('')
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [showLogs, setShowLogs] = useState(true)
  const [useRealAI, setUseRealAI] = useState(false)
  const logIdCounter = useRef(0)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const addLog = (type: LogEntry['type'], message: string, data?: any) => {
    const entry: LogEntry = {
      id: logIdCounter.current++,
      timestamp: new Date().toLocaleTimeString(),
      type,
      message,
      data
    }
    setLogs(prev => [...prev, entry])
  }

  useEffect(() => {
    addLog('info', 'Frontend initialized')
  }, [])

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      setFile(selectedFile)
      addLog('info', `File selected: ${selectedFile.name}`, {
        name: selectedFile.name,
        size: selectedFile.size,
        type: selectedFile.type
      })
      
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result as string)
        addLog('success', 'Image preview loaded')
      }
      reader.readAsDataURL(selectedFile)
    }
  }

  const handleAnalysis = async () => {
    if (!file) {
      addLog('error', 'No file selected')
      return
    }

    setLoading(true)
    addLog('info', 'Starting analysis...')

    try {
      const endpoint = useRealAI ? '/api/v1/test/test-ai' : '/api/v1/analysis/demo'
      addLog('request', `POST ${endpoint}`, {
        endpoint: endpoint,
        method: 'POST',
        fileName: file.name,
        fileSize: file.size,
        mode: useRealAI ? 'Real AI' : 'Demo'
      })

      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      
      addLog('response', 'Analysis completed', response.data)
      addLog('success', 'Analysis successful')
      setResult(response.data)
    } catch (error: any) {
      addLog('error', 'Analysis failed', {
        message: error.message,
        response: error.response?.data
      })
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  const clearAll = () => {
    setFile(null)
    setPreview('')
    setResult(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
    addLog('info', 'Cleared all data')
  }

  const getLogColor = (type: LogEntry['type']) => {
    switch (type) {
      case 'error': return 'text-red-600'
      case 'success': return 'text-green-600'
      case 'request': return 'text-blue-600'
      case 'response': return 'text-purple-600'
      default: return 'text-gray-600'
    }
  }

  return (
    <div className="container mx-auto p-4 max-w-7xl">
      <h1 className="text-3xl font-bold mb-8 text-center">DermaMed Analysis Demo</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Main Panel */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Upload Image</h2>
          
          <div className="mb-4">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-full file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100"
            />
          </div>

          {preview && (
            <div className="mb-4">
              <img 
                src={preview} 
                alt="Preview" 
                className="max-w-full h-auto rounded-lg border"
                style={{ maxHeight: '300px' }}
              />
            </div>
          )}

          <div className="mb-4">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={useRealAI}
                onChange={(e) => {
                  setUseRealAI(e.target.checked)
                  addLog('info', `Switched to ${e.target.checked ? 'Real AI' : 'Demo'} mode`)
                }}
                className="w-4 h-4"
              />
              <span className="text-sm">Use Real AI (MedGemma)</span>
            </label>
          </div>

          <div className="flex gap-2">
            <button
              onClick={handleAnalysis}
              disabled={!file || loading}
              className={`px-4 py-2 text-white rounded-lg disabled:bg-gray-400 ${
                useRealAI 
                  ? 'bg-green-600 hover:bg-green-700' 
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {loading ? 'Analyzing...' : `Analyze with ${useRealAI ? 'Real AI' : 'Demo'}`}
            </button>
            
            <button
              onClick={clearAll}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              Clear
            </button>
          </div>

          {result && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="font-semibold mb-2">Analysis Result:</h3>
              <pre className="text-sm overflow-x-auto">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Console Panel */}
        <div className="bg-gray-900 rounded-lg shadow-md p-4 h-[600px] flex flex-col">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-white font-semibold">Console Logs</h2>
            <button
              onClick={() => setShowLogs(!showLogs)}
              className="text-gray-400 hover:text-white text-sm"
            >
              {showLogs ? 'Hide' : 'Show'}
            </button>
          </div>
          
          {showLogs && (
            <div className="flex-1 overflow-y-auto font-mono text-sm">
              {logs.map(log => (
                <div key={log.id} className="mb-1">
                  <span className="text-gray-500">[{log.timestamp}]</span>{' '}
                  <span className={getLogColor(log.type)}>{log.type.toUpperCase()}</span>{' '}
                  <span className="text-gray-300">{log.message}</span>
                  {log.data && (
                    <pre className="text-xs text-gray-400 ml-4">
                      {JSON.stringify(log.data, null, 2)}
                    </pre>
                  )}
                </div>
              ))}
              {logs.length === 0 && (
                <div className="text-gray-500">No logs yet...</div>
              )}
            </div>
          )}
          
          <div className="mt-2 pt-2 border-t border-gray-700 flex justify-between">
            <button
              onClick={() => setLogs([])}
              className="text-sm text-gray-400 hover:text-white"
            >
              Clear Console
            </button>
            <button
              onClick={() => {
                const logText = logs.map(log => 
                  `[${log.timestamp}] ${log.type.toUpperCase()} ${log.message}${
                    log.data ? '\n' + JSON.stringify(log.data, null, 2) : ''
                  }`
                ).join('\n\n')
                navigator.clipboard.writeText(logText)
                addLog('info', 'Console logs copied to clipboard')
              }}
              className="text-sm text-gray-400 hover:text-white"
            >
              Copy All Logs
            </button>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <div className="mt-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <p className="text-sm text-yellow-800">
          <strong>Disclaimer:</strong> This is a demo system for testing purposes only. 
          Not approved for diagnostic use.
        </p>
      </div>
    </div>
  )
}