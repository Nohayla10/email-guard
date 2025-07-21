import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios'; // Ensure axios is installed: npm install axios

function App() {
const [emailText, setEmailText] = useState('');
  const [scanResult, setScanResult] = useState(null);
  const [scanHistory, setScanHistory] = useState([]); 
  const [loadingScan, setLoadingScan] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [error, setError] = useState(null);

  
  const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';
  const API_KEY = process.env.REACT_APP_API_KEY || "your_super_secret_email_guard_key_123" ; 

  // Function to fetch scan history
   const fetchScanHistory = async () => {
    setLoadingHistory(true);
    setError(null); 
    try {
      const response = await axios.get(
        `${API_BASE_URL}/history`,
        {
          headers: {
            'Authorization': `Bearer ${API_KEY}`
          }
        }
      );     
      setScanHistory(response.data.history); 
    } catch (err) {
      console.error("Error fetching scan history:", err);
      if (err.response) {
        setError(err.response.data.error || 'An error occurred fetching history.');
      } else if (err.request) {
        setError('No response from API when fetching history. Is the backend running?');
      } else {
        setError('Error setting up the history request.');
      }
    } finally {
      setLoadingHistory(false);
    }
  };


  useEffect(() => {
    fetchScanHistory();
  }, []); 
  const handleScanEmail = async () => {
    setLoadingScan(true);
    setScanResult(null);
    setError(null); 

    try {
      const response = await axios.post(
        
        `${API_BASE_URL}/scan`,
        { email_text: emailText },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${API_KEY}`
          }
        }
      );
      setScanResult(response.data);

      fetchScanHistory();
    } catch (err) {
      console.error("Error scanning email:", err);
      if (err.response) {
        setError(err.response.data.error || 'An error occurred with the API response.');
      } else if (err.request) {
        setError('No response from API. Is the backend running?');
      } else {
        
        setError('Error setting up the request.');
      }
    } finally {
      setLoadingScan(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Email Guard - AI Scanner</h1>
        <p className="subtitle">Protecting your inbox with intelligent email analysis</p>
      </header>
      <main>
        <section className="input-section card">
          <h2>Enter Email Text to Scan:</h2>
          <textarea
            rows="10"
            cols="80"
            placeholder="Paste your email content here..."
            value={emailText}
            onChange={(e) => setEmailText(e.target.value)}
          ></textarea>
          <button onClick={handleScanEmail} disabled={loadingScan || !emailText.trim()}>
            {loadingScan ? 'Scanning...' : 'Scan Email'}
          </button>
        </section>

        {error && (
          <section className="error-message card">
            <h3>Error:</h3>
            <p>{error}</p>
          </section>
        )}

        {scanResult && (
          <section className="result-section card">
            <h2>Scan Result:</h2>
            <p><strong>Classification:</strong> <span className={`classification-${scanResult.classification}`}>
                {scanResult.classification}
            </span></p>
            <p><strong>Confidence:</strong> {(scanResult.confidence * 100).toFixed(2)}%</p>
            <p><strong>Explanation:</strong> {scanResult.explanation}</p>
          </section>
        )}

        <section className="history-section card">
          <div className="history-header">
            <h2>Scan History</h2>
            <button onClick={fetchScanHistory} disabled={loadingHistory}>
              {loadingHistory ? 'Refreshing...' : 'Refresh History'}
            </button>
          </div>
          {scanHistory.length === 0 && !loadingHistory && <p>No scan history yet. Scan an email to see results here!</p>}
          {loadingHistory && <p>Loading history...</p>}

          <div className="history-list">
            {/* Map over scanHistory to display each entry */}
            {scanHistory.map((entry, index) => (
              <div key={index} className="history-item">
                <p><strong>Type:</strong> <span className={`classification-${entry.classification}`}>{entry.classification}</span></p>
                <p><strong>Confidence:</strong> {(entry.confidence * 100).toFixed(2)}%</p>
                {/* Use 'input' from backend, shorten it, or create 'text_snippet' in backend */}
                <p><strong>Snippet:</strong> {entry.input ? entry.input.substring(0, 100) + (entry.input.length > 100 ? '...' : '') : 'N/A'}</p>
                <p className="timestamp">{entry.timestamp ? new Date(entry.timestamp).toLocaleString() : 'N/A'}</p>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;