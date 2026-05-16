import { useState } from 'react'
import './ReleasePlanningForm.css'

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1'

function ReleasePlanningForm() {
  const [formData, setFormData] = useState({
    github_repo: '',
    jira_sprint: '',
  })
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch(`${API_BASE_URL}/release-planning/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message || 'Failed to analyze release readiness')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981'
    if (score >= 60) return '#f59e0b'
    return '#ef4444'
  }

  const getPriorityColor = (priority) => {
    const colors = {
      critical: '#ef4444',
      high: '#f59e0b',
      medium: '#3b82f6',
      low: '#6b7280',
    }
    return colors[priority] || '#6b7280'
  }

  return (
    <div className="release-planning-container">
      <div className="form-section">
        <h2>🚀 Release Planning Analysis</h2>
        <p className="form-description">
          Point the platform to a GitHub Repo and Jira Sprint to get AI-powered release readiness insights
        </p>

        <form onSubmit={handleSubmit} className="planning-form">
          <div className="form-group">
            <label htmlFor="github_repo">
              <span className="label-icon">📦</span>
              GitHub Repository
            </label>
            <input
              type="text"
              id="github_repo"
              name="github_repo"
              value={formData.github_repo}
              onChange={handleChange}
              placeholder="owner/repository"
              required
              disabled={loading}
            />
            <span className="input-hint">Example: mycompany/api-service</span>
          </div>

          <div className="form-group">
            <label htmlFor="jira_sprint">
              <span className="label-icon">📋</span>
              Jira Sprint
            </label>
            <input
              type="text"
              id="jira_sprint"
              name="jira_sprint"
              value={formData.jira_sprint}
              onChange={handleChange}
              placeholder="SPRINT-123"
              required
              disabled={loading}
            />
            <span className="input-hint">Example: SPRINT-123 or Sprint 45</span>
          </div>

          <button type="submit" className="analyze-button" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner"></span>
                Analyzing...
              </>
            ) : (
              <>
                <span>🔍</span>
                Analyze Release Readiness
              </>
            )}
          </button>
        </form>

        {error && (
          <div className="error-message">
            <span>⚠️</span>
            {error}
          </div>
        )}
      </div>

      {result && (
        <div className="results-section">
          <div className="score-card">
            <div className="score-header">
              <h3>Release Readiness Score</h3>
              <span className="confidence">
                Confidence: {(result.confidence_score * 100).toFixed(0)}%
              </span>
            </div>
            <div
              className="score-value"
              style={{ color: getScoreColor(result.readiness_score) }}
            >
              {result.readiness_score}%
            </div>
            <div className="score-details">
              <div className="detail-item">
                <span className="detail-label">GitHub Repo</span>
                <span className="detail-value">{result.github_repo}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Jira Sprint</span>
                <span className="detail-value">{result.jira_sprint}</span>
              </div>
            </div>
          </div>

          <div className="analysis-grid">
            <div className="analysis-card">
              <h4>📊 Ticket Analysis</h4>
              <div className="stats-grid">
                <div className="stat">
                  <span className="stat-value">{result.ticket_analysis.total_tickets}</span>
                  <span className="stat-label">Total Tickets</span>
                </div>
                <div className="stat">
                  <span className="stat-value success">{result.ticket_analysis.done}</span>
                  <span className="stat-label">Done</span>
                </div>
                <div className="stat">
                  <span className="stat-value warning">{result.ticket_analysis.in_progress}</span>
                  <span className="stat-label">In Progress</span>
                </div>
                <div className="stat">
                  <span className="stat-value danger">{result.ticket_analysis.blocked}</span>
                  <span className="stat-label">Blocked</span>
                </div>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${result.ticket_analysis.completion_percentage}%` }}
                ></div>
              </div>
              <p className="progress-text">
                {result.ticket_analysis.completion_percentage}% Complete
              </p>
            </div>

            <div className="analysis-card">
              <h4>💻 Repository Health</h4>
              <div className="health-items">
                <div className="health-item">
                  <span className="health-label">Build Status</span>
                  <span className={`health-badge ${result.repo_health.build_status}`}>
                    {result.repo_health.build_status}
                  </span>
                </div>
                <div className="health-item">
                  <span className="health-label">Test Coverage</span>
                  <span className="health-value">{result.repo_health.test_coverage}%</span>
                </div>
                <div className="health-item">
                  <span className="health-label">Code Quality</span>
                  <span className="health-value">{result.repo_health.code_quality_score}/10</span>
                </div>
                <div className="health-item">
                  <span className="health-label">Open PRs</span>
                  <span className="health-value">{result.repo_health.open_prs}</span>
                </div>
              </div>
            </div>
          </div>

          {result.circular_dependencies.length > 0 && (
            <div className="circular-deps-card">
              <h4>🔄 Circular Dependencies Detected</h4>
              <p className="warning-text">
                Found {result.circular_dependencies.length} circular dependency chain(s) that must be resolved:
              </p>
              {result.circular_dependencies.map((cycle, idx) => (
                <div key={idx} className="dependency-cycle">
                  <span className="cycle-icon">⚠️</span>
                  <span className="cycle-path">{cycle.join(' → ')}</span>
                </div>
              ))}
            </div>
          )}

          {result.issues.length > 0 && (
            <div className="issues-card">
              <h4>⚠️ Issues Identified</h4>
              <ul className="issues-list">
                {result.issues.map((issue, idx) => (
                  <li key={idx} className="issue-item">
                    <span className="issue-bullet">•</span>
                    {issue}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="recommendations-card">
            <h4>💡 Recommendations</h4>
            <div className="recommendations-list">
              {result.recommendations.map((rec, idx) => (
                <div key={idx} className="recommendation-item">
                  <div className="rec-header">
                    <h5>{rec.title}</h5>
                    <span
                      className="priority-badge"
                      style={{ backgroundColor: getPriorityColor(rec.priority) }}
                    >
                      {rec.priority}
                    </span>
                  </div>
                  <p className="rec-description">{rec.description}</p>
                  {rec.action && (
                    <div className="rec-action">
                      <strong>Action:</strong> {rec.action}
                    </div>
                  )}
                  {rec.impact && (
                    <div className="rec-impact">
                      <strong>Impact:</strong> {rec.impact}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ReleasePlanningForm

// Made with Bob
