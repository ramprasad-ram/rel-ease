import { useEffect, useMemo, useState } from 'react'
import './App.css'
import ReleasePlanningForm from './components/ReleasePlanningForm'
import PreFlightCheck from './components/PreFlightCheck'
import CanaryDashboard from './components/CanaryDashboard'

const fallbackData = {
  platform: { name: 'Release Orchestration Platform', version: '1.0.0', status: 'demo' },
  summary: {
    release_confidence: 87,
    healthy_release_ratio: 78,
    workflow_progress: 72,
    active_deployments: 3,
    avg_lead_time_hours: 4.6,
  },
  deployment_state_counts: {
    approved: 3,
    deploying: 2,
    deployed: 4,
    failed: 1,
    monitoring: 1,
  },
  workflow_status_counts: {
    completed: 3,
    running: 1,
    pending: 2,
    failed: 0,
  },
  latest_deployments: [
    { id: '1', name: 'deployment-api-21', version: '2.4.1', state: 'deployed', environment: 'production', platform: 'kubernetes', updated_at: new Date().toISOString() },
    { id: '2', name: 'deployment-web-15', version: '2.4.1', state: 'monitoring', environment: 'staging', platform: 'aws', updated_at: new Date().toISOString() },
    { id: '3', name: 'deployment-worker-08', version: '2.3.9', state: 'approved', environment: 'production', platform: 'docker', updated_at: new Date().toISOString() },
  ],
  latest_workflows: [
    { id: 'w1', name: 'Sequential Deployment Workflow', type: 'sequential', status: 'running', current_step: 2, updated_at: new Date().toISOString() },
    { id: 'w2', name: 'Rollback Workflow', type: 'rollback', status: 'completed', current_step: 4, updated_at: new Date().toISOString() },
  ],
  agent_cards: [
    { name: 'Release Planning Agent', status: 'ready', summary: 'Analyzes sprint scope and release blockers.' },
    { name: 'CI/CD Validation Agent', status: 'running', summary: 'Evaluates tests, scans, and build quality.' },
    { name: 'Environment Monitoring Agent', status: 'watching', summary: 'Detects configuration drift and infra issues.' },
    { name: 'Deployment Agent', status: 'scheduled', summary: 'Executes safe deployment strategies.' },
    { name: 'Rollback Agent', status: 'standby', summary: 'Protects production through autonomous rollback.' },
    { name: 'Change Communication Agent', status: 'ready', summary: 'Prepares stakeholder updates and release notes.' },
    { name: 'Postmortem Agent', status: 'learning', summary: 'Extracts insights from release failures.' },
  ],
  timeline: [
    { phase: 'Plan', detail: 'Map Jira scope, risks, and dependencies' },
    { phase: 'Validate', detail: 'Confirm CI/CD, test, and scan readiness' },
    { phase: 'Monitor', detail: 'Check infra health and config drift' },
    { phase: 'Deploy', detail: 'Promote canary/rolling/blue-green release' },
    { phase: 'Rollback', detail: 'Auto-revert when anomaly thresholds are breached' },
    { phase: 'Communicate', detail: 'Share release notes and deployment summaries' },
  ],
}

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1/demo/dashboard'

function App() {
  const [dashboardData, setDashboardData] = useState(fallbackData)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await fetch(API_BASE_URL)
        if (!response.ok) {
          throw new Error(`Request failed with status ${response.status}`)
        }

        const data = await response.json()
        setDashboardData(data)
        setError('')
      } catch (fetchError) {
        setError('Backend demo API unavailable. Showing fallback demo data.')
      } finally {
        setLoading(false)
      }
    }

    fetchDashboard()
  }, [])

  const planningSignals = useMemo(
    () => [
      {
        label: 'Release confidence',
        value: `${dashboardData.summary.release_confidence}%`,
        status: dashboardData.summary.release_confidence >= 80 ? 'healthy' : 'warning',
      },
      {
        label: 'Healthy release ratio',
        value: `${dashboardData.summary.healthy_release_ratio}%`,
        status: dashboardData.summary.healthy_release_ratio >= 70 ? 'healthy' : 'warning',
      },
      {
        label: 'Active deployments',
        value: `${dashboardData.summary.active_deployments}`,
        status: dashboardData.summary.active_deployments <= 3 ? 'healthy' : 'warning',
      },
    ],
    [dashboardData],
  )

  const pipelineChecks = useMemo(
    () => [
      {
        name: 'Completed workflows',
        detail: `${dashboardData.workflow_status_counts.completed ?? 0} workflow runs completed successfully`,
        state: 'pass',
      },
      {
        name: 'Running workflows',
        detail: `${dashboardData.workflow_status_counts.running ?? 0} workflow currently executing`,
        state: 'watch',
      },
      {
        name: 'Failed deployments',
        detail: `${dashboardData.deployment_state_counts.failed ?? 0} deployment requires attention`,
        state: (dashboardData.deployment_state_counts.failed ?? 0) > 0 ? 'pending' : 'pass',
      },
      {
        name: 'Average lead time',
        detail: `${dashboardData.summary.avg_lead_time_hours} hours from creation to latest state transition`,
        state: 'pass',
      },
    ],
    [dashboardData],
  )

  const impactMetrics = useMemo(
    () => [
      { value: `${dashboardData.summary.workflow_progress}%`, label: 'workflow progress visibility' },
      { value: `${dashboardData.summary.release_confidence}%`, label: 'production confidence score' },
      { value: `${dashboardData.summary.avg_lead_time_hours}h`, label: 'average release lead time' },
    ],
    [dashboardData],
  )

  return (
    <main className="app-shell">
      <section className="hero-panel">
        <div className="hero-copy">
          <p className="eyebrow">Agentic AI release orchestration platform</p>
          <h1>Autonomous release coordination for safer and faster deployments.</h1>
          <p className="hero-text">
            Live operational view for release planning, validation, environment health,
            deployment execution, rollback readiness, and stakeholder communication.
          </p>

          <div className="hero-actions">
            <a href="#agents" className="primary-action">
              Explore agent network
            </a>
            <a href="#operations" className="secondary-action">
              View live operations
            </a>
          </div>

          <div className="hero-meta">
            <span className="hero-meta-chip">
              {loading ? 'Loading live orchestration data...' : `Connected to ${dashboardData.platform.name}`}
            </span>
            {error ? <span className="hero-meta-chip warning-chip">{error}</span> : null}
          </div>

          <div className="signal-grid">
            {planningSignals.map((signal) => (
              <article key={signal.label} className={`signal-card ${signal.status}`}>
                <span>{signal.label}</span>
                <strong>{signal.value}</strong>
              </article>
            ))}
          </div>
        </div>

        <div className="hero-visual">
          <div className="status-card">
            <div className="status-header">
              <span className="status-dot"></span>
              Live release readiness overview
            </div>
            <div className="status-score">
              <strong>{dashboardData.summary.release_confidence}%</strong>
              <span>Production release confidence</span>
            </div>
            <div className="mini-metrics">
              <div>
                <span>Workflow progress</span>
                <strong>{dashboardData.summary.workflow_progress}%</strong>
              </div>
              <div>
                <span>Healthy release ratio</span>
                <strong>{dashboardData.summary.healthy_release_ratio}%</strong>
              </div>
              <div>
                <span>Lead time</span>
                <strong>{dashboardData.summary.avg_lead_time_hours}h</strong>
              </div>
            </div>
          </div>

          <div className="flow-card">
            <p>Live orchestration path</p>
            <div className="flow-track">
              {dashboardData.timeline.slice(0, 4).map((step) => (
                <span key={step.phase}>{step.phase}</span>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section id="operations" className="dashboard-grid">
        <article className="panel">
          <div className="section-heading">
            <p className="eyebrow">Validation control room</p>
            <h2>Release gates and CI/CD intelligence</h2>
          </div>
          <div className="checks-list">
            {pipelineChecks.map((check) => (
              <div key={check.name} className="check-row">
                <span className={`badge ${check.state}`}>{check.state}</span>
                <div>
                  <h3>{check.name}</h3>
                  <p>{check.detail}</p>
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="section-heading">
            <p className="eyebrow">Latest deployment activity</p>
            <h2>Recently updated release candidates</h2>
          </div>
          <div className="activity-list">
            {dashboardData.latest_deployments.map((deployment) => (
              <article key={deployment.id} className="activity-card">
                <div className="activity-topline">
                  <h3>{deployment.name}</h3>
                  <span className={`agent-status state-${deployment.state}`}>{deployment.state}</span>
                </div>
                <p>
                  v{deployment.version} • {deployment.environment} • {deployment.platform}
                </p>
              </article>
            ))}
          </div>
        </article>
      </section>

      <section className="dashboard-grid">
        <article className="panel">
          <div className="section-heading">
            <p className="eyebrow">Business impact</p>
            <h2>Why teams adopt autonomous release orchestration</h2>
          </div>
          <div className="impact-grid">
            {impactMetrics.map((metric) => (
              <div key={metric.label} className="impact-card">
                <strong>{metric.value}</strong>
                <span>{metric.label}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <div className="section-heading">
            <p className="eyebrow">Workflow activity</p>
            <h2>Current orchestrated workflow runs</h2>
          </div>
          <div className="activity-list">
            {dashboardData.latest_workflows.map((workflow) => (
              <article key={workflow.id} className="activity-card">
                <div className="activity-topline">
                  <h3>{workflow.name}</h3>
                  <span className={`agent-status state-${workflow.status}`}>{workflow.status}</span>
                </div>
                <p>
                  {workflow.type} • current step {workflow.current_step + 1}
                </p>
              </article>
            ))}
          </div>
        </article>
      </section>

      <section id="agents" className="agents-section">
        <div className="section-heading">
          <p className="eyebrow">Multi-agent network</p>
          <h2>Specialized agents for every stage of the release cycle</h2>
        </div>

        <div className="agents-grid">
          {dashboardData.agent_cards.map((agent) => (
            <article key={agent.name} className="agent-card">
              <div className="agent-card-header">
                <h3>{agent.name}</h3>
                <span className={`agent-status state-${agent.status}`}>{agent.status}</span>
              </div>
              <p>{agent.summary}</p>
            </article>
          ))}
        </div>
      </section>

      <section id="timeline" className="timeline-section">
        <div className="section-heading">
          <p className="eyebrow">Release execution flow</p>
          <h2>From planning to post-deployment protection</h2>
        </div>

        <div className="timeline">
          {dashboardData.timeline.map((step, index) => (
            <article key={step.phase} className="timeline-card">
              <div className="timeline-index">0{index + 1}</div>
              <div>
                <h3>{step.phase}</h3>
                <p>{step.detail}</p>
                <span>Autonomous orchestration phase</span>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section id="release-planning" className="release-planning-section">
        <ReleasePlanningForm />
      </section>

      <section id="pre-flight" className="pre-flight-section">
        <PreFlightCheck />
      </section>

      <section id="canary-deployment" className="canary-deployment-section">
        <CanaryDashboard />
      </section>
    </main>
  )
}

export default App
