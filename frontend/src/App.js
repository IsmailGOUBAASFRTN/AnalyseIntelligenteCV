import React, { useState } from 'react';
import axios from 'axios';
import AnalysisForm from './components/AnalysisForm';
import ResultsDisplay from './components/ResultsDisplay';
import './App.css';

function App() {
    const [analysisResult, setAnalysisResult] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const handleAnalysis = async (formData) => {
        setIsLoading(true);
        setError('');
        setAnalysisResult(null);
        try {
            const response = await axios.post('http://127.0.0.1:8000/api/analyze', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            });
            setAnalysisResult(response.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Une erreur est survenue.');
        }
        setIsLoading(false);
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>Analyseur Intelligent de CV</h1>
            </header>
            <main>
                <AnalysisForm onAnalyze={handleAnalysis} isLoading={isLoading} />
                {isLoading && <div className="loader">Analyse en cours...</div>}
                {error && <div className="error-message">{error}</div>}
                {analysisResult && <ResultsDisplay result={analysisResult} />}
            </main>
        </div>
    );
}

export default App;