import React, { useState } from 'react';
import axios from 'axios';
import AnalysisForm from './components/AnalysisForm';
import ResultsDisplay from './components/ResultsDisplay';
import './App.css';

function App() {
    const [analysisResult, setAnalysisResult] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

    const handleAnalysis = async (formData) => {
        setIsLoading(true);
        setError('');
        setAnalysisResult(null);
        try {
            const response = await axios.post(`${API_BASE_URL}/api/analyze`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                timeout: 120000,
            });
            setAnalysisResult(response.data);
        } catch (err) {
            if (err.code === 'ECONNABORTED') {
                setError('La requête a expiré. Veuillez réessayer.');
            } else if (err.response?.status === 413) {
                setError('Le fichier est trop volumineux (maximum 10 MB).');
            } else if (err.response?.status === 415) {
                setError('Type de fichier non supporté. Formats acceptés : PDF, DOCX, TXT.');
            } else {
                setError(err.response?.data?.detail || 'Une erreur est survenue. Veuillez réessayer.');
            }
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