import React, { useState } from 'react';

const AnalysisForm = ({ onAnalyze, isLoading }) => {
    const [jobTitle, setJobTitle] = useState('');
    const [jobDescriptionFile, setJobDescriptionFile] = useState(null);
    const [cvFiles, setCvFiles] = useState([]);

    const handleSubmit = (e) => {
        e.preventDefault();
        const formData = new FormData();
        if (jobTitle) formData.append('job_title', jobTitle);
        if (jobDescriptionFile) formData.append('job_description_file', jobDescriptionFile);
        cvFiles.forEach(cv => {
            formData.append('cv_files', cv);
        });
        onAnalyze(formData);
    };

    return (
        <form onSubmit={handleSubmit} className="analysis-form">
            <h2>1. Définir le Poste</h2>
            <div className="form-group">
                <label htmlFor="job-title">Intitulé de poste</label>
                <input 
                    type="text" 
                    id="job-title"
                    value={jobTitle}
                    onChange={(e) => setJobTitle(e.target.value)} 
                />
            </div>
            <div className="form-group or-separator">OU</div>
            <div className="form-group">
                <label htmlFor="job-desc">Importer une fiche de poste (PDF/Word)</label>
                <input 
                    type="file"
                    id="job-desc"
                    accept=".pdf,.doc,.docx"
                    onChange={(e) => setJobDescriptionFile(e.target.files[0])} 
                />
            </div>
            
            <h2>2. Téléverser les CV</h2>
            <div className="form-group">
                <label htmlFor="cv-files">CV (un ou plusieurs)</label>
                <input 
                    type="file" 
                    id="cv-files"
                    accept=".pdf,.doc,.docx"
                    multiple 
                    onChange={(e) => setCvFiles([...e.target.files])} 
                    required
                />
            </div>

            <button type="submit" disabled={isLoading}>{isLoading ? 'Analyse...' : 'Lancer l\'analyse'}</button>
        </form>
    );
};

export default AnalysisForm;