import React from 'react';
import RadarChart from './RadarChart';

const ResultsDisplay = ({ result }) => {
    const { analysis_data, cv_filename, id } = result;

    const handleExport = () => {
        window.open(`http://127.0.0.1:8000/api/export/${id}`, '_blank');
    }

    return (
        <div className="results-container">
            <h2>Résultats de l'analyse pour : {cv_filename}</h2>
            <button onClick={handleExport} className="export-button">Exporter en PDF</button>
            <div className="results-grid">
                <div className="score-card main-score">
                    <h3>Score d'Adéquation</h3>
                    <p>{analysis_data.score}%</p>
                </div>
                <div className="summary-card card">
                    <h3>Résumé</h3>
                    <p>{analysis_data.summary}</p>
                </div>
                <div className="chart-card card">
                    <h3>Notation par Catégorie</h3>
                    <RadarChart skills={analysis_data.skills_rating} />
                </div>
                <div className="strengths-card card">
                    <h3>Points Forts</h3>
                    <ul>{analysis_data.strengths.map((s, i) => <li key={i}>{s}</li>)}</ul>
                </div>
                <div className="improvements-card card">
                    <h3>Axes d'Amélioration</h3>
                    <ul>{analysis_data.improvements.map((i, idx) => <li key={idx}>{i}</li>)}</ul>
                </div>
                <div className="keywords-card card">
                     <h3>Mots-clés Correspondants</h3>
                     <div className="keyword-tags">
                        {analysis_data.matching_keywords.map((kw, i) => <span key={i} className="keyword-tag">{kw}</span>)}
                     </div>
                </div>
                 <div className="alternatives-card card">
                    <h3>Postes Alternatifs Suggérés</h3>
                    <ul>{analysis_data.alternative_jobs.map((job, i) => <li key={i}>{job}</li>)}</ul>
                </div>
            </div>
        </div>
    );
};

export default ResultsDisplay;