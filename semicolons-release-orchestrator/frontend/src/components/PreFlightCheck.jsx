import { useState } from 'react'
import './PreFlightCheck.css'

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1'

function PreFlightCheck() {
  const [deploymentId, setDeploymentId] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const handlePrepareDeployment = async (e) => {
    e.preventDefault()
    
    if (!deploymentId.trim()) {
      setError('Please enter a deployment ID')
      return
    }

    setLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch(
        `${API_BASE_URL}/pre-flight/deployments/${deploymentId}/pre-flight-check`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      )

      if (!response.ok) {
        throw new Error(`Validation failed: ${response.statusText}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message || 'Failed to run pre-flight validation')
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981'
    if (score >= 60) return '#f59e0b'
    return '#ef4444'
  }

  const getSeverityColor = (severity) => {
    const colors = {
      critical: '#ef4444',
      warning: '#f59e0b',
      normal: '#10b981',
    }
    return colors[severity] || '#6b7280'
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
    <div className="preflight-container">
      <div className="preflight-form-section">
        <h2>🛫 Pre-Flight Deployment Check</h2>
        <p className="preflight-description">
          Validate deployment readiness by analyzing CI run history, detecting memory leaks, and identifying performance regressions
        </p>

        <form onSubmit={handlePrepareDeployment} className="preflight-form">
          <div className="form-group">
            <label htmlFor="deployment_id">
              <span className="label-icon">🚀</span>
              Deployment ID
            </label>
            <input
              type="text"
              id="deployment_id"
              value={deploymentId}
              onChange={(e) => setDeploymentId(e.target.value)}
              placeholder="deployment-123"
              required
              disabled={loading}
            />
            <span className="input-hint">Example: deployment-123 or prod-release-v2.1</span>
          </div>

          <button type="submit" className="prepare-button" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner"></span>
                Analyzing CI Runs...
              </>
            ) : (
              <>
                <span>🔍</span>
                Prepare Deployment
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
        <div className="preflight-results">
          <div className="validation-score-card">
            <div className="score-header">
              <h3>Validation Score</h3>
              <span className={`ready-badge ${result.ready_to_deploy ? 'ready' : 'not-ready'}`}>
                {result.ready_to_deploy ? '✅ Ready to Deploy' : '❌ Not Ready'}
              </span>
            </div>
            <div
              className="score-value"
              style={{ color: getScoreColor(result.validation_score) }}
            >
              {result.validation_score}%
            </div>
            <div className="score-meta">
              <span>Analyzed {result.ci_runs_analyzed} CI runs</span>
              <span>Confidence: {(result.confidence_score * 100).toFixed(0)}%</span>
            </div>
          </div>

          <div className="analysis-sections">
            {/* Memory Analysis */}
            <div className="analysis-section">
              <h4>💾 Memory Analysis</h4>
              <div className="metrics-grid">
                <div className="metric-item">
                  <span className="metric-label">Trend</span>
                  <span className={`metric-value ${result.memory_analysis.trend === 'increasing' ? 'warning' : 'success'}`}>
                    {result.memory_analysis.trend}
                  </span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Change</span>
                  <span className={`metric-value ${result.memory_analysis.increase_percent > 10 ? 'danger' : 'normal'}`}>
                    {result.memory_analysis.increase_percent > 0 ? '+' : ''}
                    {result.memory_analysis.increase_percent}%
                  </span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Current</span>
                  <span className="metric-value">{result.memory_analysis.newest_memory_mb} MB</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Peak</span>
                  <span className="metric-value">{result.memory_analysis.peak_memory_mb} MB</span>
                </div>
              </div>
              
              {result.memory_analysis.leaky_modules && result.memory_analysis.leaky_modules.length > 0 && (
                <div className="leak-warning">
                  <span className="warning-icon">⚠️</span>
                  <div>
                    <strong>Potential Memory Leak Detected</strong>
                    <p>Modules: {result.memory_analysis.leaky_modules.join(', ')}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Performance Analysis */}
            <div className="analysis-section">
              <h4>⚡ Performance Analysis</h4>
              <div className="metrics-grid">
                <div className="metric-item">
                  <span className="metric-label">Trend</span>
                  <span className={`metric-value ${result.performance_analysis.trend === 'degrading' ? 'warning' : 'success'}`}>
                    {result.performance_analysis.trend}
                  </span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Change</span>
                  <span className={`metric-value ${result.performance_analysis.degradation_percent > 10 ? 'danger' : 'normal'}`}>
                    {result.performance_analysis.degradation_percent > 0 ? '+' : ''}
                    {result.performance_analysis.degradation_percent}%
                  </span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Current RT</span>
                  <span className="metric-value">{result.performance_analysis.newest_response_time_ms} ms</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Average RT</span>
                  <span className="metric-value">{result.performance_analysis.average_response_time_ms} ms</span>
                </div>
              </div>
            </div>

            {/* Test Coverage */}
            <div className="analysis-section">
              <h4>🧪 Test Coverage</h4>
              <div className="coverage-display">
                <div className="coverage-bar">
                  <div
                    className="coverage-fill"
                    style={{
                      width: `${result.coverage_analysis.current_coverage}%`,
                      backgroundColor: result.coverage_analysis.meets_threshold ? '#10b981' : '#f59e0b'
                    }}
                  ></div>
                </div>
                <div className="coverage-stats">
                  <span className="coverage-value">{result.coverage_analysis.current_coverage}%</span>
                  <span className={`coverage-status ${result.coverage_analysis.meets_threshold ? 'pass' : 'warn'}`}>
                    {result.coverage_analysis.meets_threshold ? '✓ Meets threshold' : '⚠ Below 80%'}
                  </span>
                </div>
              </div>
            </div>

            {/* Build Stability */}
            <div className="analysis-section">
              <h4>🔨 Build Stability</h4>
              <div className="build-stats">
                <div className="build-stat">
                  <span className="build-label">Success Rate</span>
                  <span className={`build-value ${result.build_analysis.is_stable ? 'success' : 'warning'}`}>
                    {result.build_analysis.success_rate}%
                  </span>
                </div>
                <div className="build-stat">
                  <span className="build-label">Successful</span>
                  <span className="build-value success">{result.build_analysis.successful_runs}</span>
                </div>
                <div className="build-stat">
                  <span className="build-label">Failed</span>
                  <span className="build-value danger">{result.build_analysis.failed_runs}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Issues */}
          {result.issues && result.issues.length > 0 && (
            <div className="issues-section">
              <h4>⚠️ Issues Detected</h4>
              <div className="issues-list">
                {result.issues.map((issue, idx) => (
                  <div
                    key={idx}
                    className="issue-card"
                    style={{ borderLeftColor: getSeverityColor(issue.severity) }}
                  >
                    <div className="issue-header">
                      <h5>{issue.title}</h5>
                      <span
                        className="severity-badge"
                        style={{ backgroundColor: getSeverityColor(issue.severity) }}
                      >
                        {issue.severity}
                      </span>
                    </div>
                    <p className="issue-description">{issue.description}</p>
                    {issue.metric && (
                      <div className="issue-metric">
                        <strong>Metric:</strong> {issue.metric}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          <div className="recommendations-section">
            <h4>💡 Recommendations</h4>
            <div className="recommendations-list">
              {result.recommendations.map((rec, idx) => (
                <div key={idx} className="recommendation-card">
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

export default PreFlightCheck

// Made with Bob
