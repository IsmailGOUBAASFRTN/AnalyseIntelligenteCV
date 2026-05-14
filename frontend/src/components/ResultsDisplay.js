import React from 'react';
import RadarChart from './RadarChart';

const recommendationColor = {
    'Fortement recommandé': '#22c55e',
    'Recommandé': '#84cc16',
    'À considérer': '#f59e0b',
    'Non recommandé': '#ef4444',
};

const ResultsDisplay = ({ result }) => {
    const { analysis_data, cv_filename, id } = result;

    if (analysis_data?.error) {
        return (
            <div className="results-container">
                <h2>Résultats de l'analyse pour : {cv_filename}</h2>
                <div className="error-message">
                    <strong>Erreur de l'IA :</strong> {analysis_data.error}
                </div>
            </div>
        );
    }

    const strengths = analysis_data?.strengths || [];
    const improvements = analysis_data?.improvements || [];
    const matchingKeywords = analysis_data?.matching_keywords || [];
    const missingKeywords = analysis_data?.missing_keywords || [];
    const alternativeJobs = analysis_data?.alternative_jobs || [];
    const redFlags = analysis_data?.red_flags || [];
    const technicalGaps = analysis_data?.technical_gaps || [];
    const coverLetterTips = analysis_data?.cover_letter_tips || [];
    const interviewQuestions = analysis_data?.interview_questions || [];
    const recommendation = analysis_data?.hiring_recommendation;
    const recColor = recommendationColor[recommendation] || '#6b7280';

    const handleExport = () => {
        window.open(`http://127.0.0.1:8000/api/export/${id}`, '_blank');
    };

    const handlePrint = () => {
        window.print();
    };

    return (
        <div className="results-container">
            <h2>Résultats de l'analyse pour : {cv_filename}</h2>
            <div className="action-buttons">
                <button onClick={handleExport} className="export-button">⬇️ Télécharger PDF</button>
                <button onClick={handlePrint} className="print-button">🖨️ Imprimer</button>
            </div>

            <div className="results-grid">

                {/* Score + Recommandation */}
                <div className="score-card main-score">
                    <h3>Score d'Adéquation</h3>
                    <p>{analysis_data?.score ?? '—'}%</p>
                    {analysis_data?.score_justification && (
                        <small>{analysis_data.score_justification}</small>
                    )}
                </div>

                <div className="card" style={{ borderLeft: `4px solid ${recColor}` }}>
                    <h3>Verdict Recruteur</h3>
                    {recommendation && (
                        <p style={{ color: recColor, fontWeight: 'bold', fontSize: '1.1rem' }}>
                            {recommendation}
                        </p>
                    )}
                    {analysis_data?.seniority_level && (
                        <p><strong>Niveau :</strong> {analysis_data.seniority_level}</p>
                    )}
                    {analysis_data?.years_of_experience !== undefined && (
                        <p><strong>Expérience estimée :</strong> {analysis_data.years_of_experience} an(s)</p>
                    )}
                    {analysis_data?.experience_gap && (
                        <p><strong>Écart :</strong> {analysis_data.experience_gap}</p>
                    )}
                </div>

                {/* Résumé */}
                <div className="summary-card card" style={{ gridColumn: '1 / -1' }}>
                    <h3>Résumé de l'Analyse</h3>
                    <p>{analysis_data?.summary}</p>
                </div>

                {/* Radar */}
                <div className="chart-card card">
                    <h3>Notation par Catégorie</h3>
                    <RadarChart skills={analysis_data?.skills_rating} />
                </div>

                {/* Points forts */}
                <div className="strengths-card card">
                    <h3>✅ Points Forts</h3>
                    {strengths.length > 0
                        ? <ul>{strengths.map((s, i) => <li key={i}>{s}</li>)}</ul>
                        : <p>Aucun point fort identifié.</p>
                    }
                </div>

                {/* Axes d'amélioration */}
                <div className="improvements-card card">
                    <h3>📈 Axes d'Amélioration</h3>
                    {improvements.length > 0
                        ? <ul>{improvements.map((item, i) => <li key={i}>{item}</li>)}</ul>
                        : <p>Aucun axe d'amélioration identifié.</p>
                    }
                </div>

                {/* Red Flags */}
                {redFlags.length > 0 && !(redFlags.length === 1 && redFlags[0].toLowerCase().includes('aucun')) && (
                    <div className="card" style={{ borderLeft: '4px solid #ef4444' }}>
                        <h3>⚠️ Points de Vigilance</h3>
                        <ul>{redFlags.map((flag, i) => <li key={i}>{flag}</li>)}</ul>
                    </div>
                )}

                {/* Lacunes techniques */}
                {technicalGaps.length > 0 && (
                    <div className="card">
                        <h3>🔧 Lacunes Techniques</h3>
                        <ul>{technicalGaps.map((gap, i) => <li key={i}>{gap}</li>)}</ul>
                    </div>
                )}

                {/* Mots-clés */}
                <div className="keywords-card card">
                    <h3>🟢 Mots-clés Correspondants</h3>
                    <div className="keyword-tags">
                        {matchingKeywords.length > 0
                            ? matchingKeywords.map((kw, i) => (
                                <span key={i} className="keyword-tag keyword-match">{kw}</span>
                              ))
                            : <p>Aucun mot-clé correspondant.</p>
                        }
                    </div>
                </div>

                <div className="keywords-card card">
                    <h3>🔴 Mots-clés Manquants</h3>
                    <div className="keyword-tags">
                        {missingKeywords.length > 0
                            ? missingKeywords.map((kw, i) => (
                                <span key={i} className="keyword-tag keyword-missing">{kw}</span>
                              ))
                            : <p>Aucun mot-clé manquant.</p>
                        }
                    </div>
                </div>

                {/* Questions d'entretien */}
                {interviewQuestions.length > 0 && (
                    <div className="card" style={{ gridColumn: '1 / -1' }}>
                        <h3>🎤 Questions d'Entretien Suggérées</h3>
                        <div className="interview-list">
                            {interviewQuestions.map((item, i) => (
                                <div key={i} className="interview-item">
                                    <p className="interview-question">
                                        <strong>Q{i + 1} :</strong> {typeof item === 'string' ? item : item.question}
                                    </p>
                                    {item.objectif && (
                                        <p className="interview-meta">
                                            <span className="interview-label">🎯 Objectif :</span> {item.objectif}
                                        </p>
                                    )}
                                    {item.reponse_attendue && (
                                        <p className="interview-meta">
                                            <span className="interview-label">✅ Réponse attendue :</span> {item.reponse_attendue}
                                        </p>
                                    )}
                                    {item.conseil_recruteur && (
                                        <p className="interview-meta interview-tip">
                                            <span className="interview-label">💡 Conseil recruteur :</span> {item.conseil_recruteur}
                                        </p>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Conseils lettre de motivation */}
                {coverLetterTips.length > 0 && (
                    <div className="card">
                        <h3>✉️ Conseils Lettre de Motivation</h3>
                        <ul>{coverLetterTips.map((tip, i) => <li key={i}>{tip}</li>)}</ul>
                    </div>
                )}

                {/* Postes alternatifs */}
                <div className="alternatives-card card">
                    <h3>💼 Postes Alternatifs Suggérés</h3>
                    {alternativeJobs.length > 0
                        ? <ul>{alternativeJobs.map((job, i) => <li key={i}>{job}</li>)}</ul>
                        : <p>Aucune suggestion disponible.</p>
                    }
                </div>

            </div>
        </div>
    );
};

export default ResultsDisplay;