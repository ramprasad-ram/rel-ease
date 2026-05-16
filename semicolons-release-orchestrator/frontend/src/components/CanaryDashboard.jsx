import { useState, useEffect, useRef } from 'react';
import './CanaryDashboard.css';

const API_BASE_URL = 'http://localhost:8000/api/v1';

function CanaryDashboard() {
  const [deploymentId, setDeploymentId] = useState('');
  const [version, setVersion] = useState('');
  const [environment, setEnvironment] = useState('production');
  const [canaryReplicas, setCanaryReplicas] = useState(1);
  const [stableReplicas, setStableReplicas] = useState(3);
  
  const [isDeploying, setIsDeploying] = useState(false);
  const [deploymentStatus, setDeploymentStatus] = useState(null);
  const [events, setEvents] = useState([]);
  const [error, setError] = useState(null);
  
  const eventSourceRef = useRef(null);

  // Cleanup EventSource on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const startCanaryDeployment = async () => {
    if (!deploymentId || !version) {
      setError('Please provide both Deployment ID and Version');
      return;
    }

    setError(null);
    setIsDeploying(true);
    setEvents([]);
    setDeploymentStatus(null);

    try {
      // Start the canary deployment
      const response = await fetch(
        `${API_BASE_URL}/canary/deployments/${deploymentId}/execute-canary`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            version,
            environment,
            canary_replicas: canaryReplicas,
            stable_replicas: stableReplicas,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to start canary deployment');
      }

      const data = await response.json();
      addEvent('info', `Canary deployment started: ${data.deployment_id}`);

      // Connect to SSE stream for real-time updates
      connectToEventStream(deploymentId);
    } catch (err) {
      setError(err.message);
      setIsDeploying(false);
    }
  };

  const connectToEventStream = (depId) => {
    // Close existing connection if any
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const eventSource = new EventSource(
      `${API_BASE_URL}/canary/deployments/${depId}/stream`
    );

    eventSource.onopen = () => {
      addEvent('success', 'Connected to deployment stream');
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.error) {
          addEvent('error', data.error);
          setError(data.error);
          setIsDeploying(false);
          eventSource.close();
          return;
        }

        if (data.event === 'connected') {
          addEvent('info', `Monitoring deployment: ${data.deployment_id}`);
        } else if (data.event === 'status_update') {
          setDeploymentStatus(data.status);
          addEvent('info', `Stage: ${data.status.current_stage} | Traffic: ${data.status.traffic_percentage}%`);
        } else if (data.event === 'stage_complete') {
          addEvent('success', `✓ Stage completed: ${data.stage} (${data.traffic_percentage}% traffic)`);
        } else if (data.event === 'deployment_complete') {
          addEvent('success', '🎉 Canary deployment completed successfully!');
          setIsDeploying(false);
          eventSource.close();
        } else if (data.event === 'deployment_failed') {
          addEvent('error', `❌ Deployment failed: ${data.reason}`);
          setError(data.reason);
          setIsDeploying(false);
          eventSource.close();
        } else if (data.event === 'rollback_triggered') {
          addEvent('warning', `⚠️ Rollback triggered: ${data.reason}`);
        }
      } catch (err) {
        console.error('Error parsing SSE data:', err);
      }
    };

    eventSource.onerror = (err) => {
      console.error('EventSource error:', err);
      addEvent('error', 'Connection to deployment stream lost');
      setIsDeploying(false);
      eventSource.close();
    };

    eventSourceRef.current = eventSource;
  };

  const addEvent = (type, message) => {
    const timestamp = new Date().toLocaleTimeString();
    setEvents((prev) => [...prev, { type, message, timestamp }]);
  };

  const getStageProgress = () => {
    if (!deploymentStatus) return 0;
    const stages = ['initializing', 'canary_10', 'canary_25', 'canary_50', 'full_rollout'];
    const currentIndex = stages.indexOf(deploymentStatus.current_stage);
    return ((currentIndex + 1) / stages.length) * 100;
  };

  const getHealthColor = (health) => {
    if (!health) return '#6b7280';
    if (health >= 95) return '#10b981';
    if (health >= 80) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className="canary-dashboard">
      <div className="deployment-form">
        <div className="dashboard-header">
          <h2>🚀 Canary Deployment Dashboard</h2>
          <p>Progressive traffic shifting with real-time monitoring</p>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="deploymentId">Deployment ID</label>
            <input
              id="deploymentId"
              type="text"
              value={deploymentId}
              onChange={(e) => setDeploymentId(e.target.value)}
              placeholder="e.g., deploy-12345"
              disabled={isDeploying}
            />
          </div>
          <div className="form-group">
            <label htmlFor="version">Version</label>
            <input
              id="version"
              type="text"
              value={version}
              onChange={(e) => setVersion(e.target.value)}
              placeholder="e.g., 2.1.0"
              disabled={isDeploying}
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="environment">Environment</label>
            <select
              id="environment"
              value={environment}
              onChange={(e) => setEnvironment(e.target.value)}
              disabled={isDeploying}
            >
              <option value="production">Production</option>
              <option value="staging">Staging</option>
              <option value="development">Development</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="canaryReplicas">Canary Replicas</label>
            <input
              id="canaryReplicas"
              type="number"
              min="1"
              max="10"
              value={canaryReplicas}
              onChange={(e) => setCanaryReplicas(parseInt(e.target.value))}
              disabled={isDeploying}
            />
          </div>
          <div className="form-group">
            <label htmlFor="stableReplicas">Stable Replicas</label>
            <input
              id="stableReplicas"
              type="number"
              min="1"
              max="10"
              value={stableReplicas}
              onChange={(e) => setStableReplicas(parseInt(e.target.value))}
              disabled={isDeploying}
            />
          </div>
        </div>

        <button
          className="start-button"
          onClick={startCanaryDeployment}
          disabled={isDeploying}
        >
          {isDeploying ? '🔄 Deploying...' : '🚀 Start Canary Deployment'}
        </button>

        {error && (
          <div className="error-message">
            <span>⚠️</span> {error}
          </div>
        )}
      </div>

      {deploymentStatus && (
        <div className="status-grid">
          <div className="status-card">
            <h3>Current Stage</h3>
            <div className="status-value stage-value">
              {deploymentStatus.current_stage.replace('_', ' ').toUpperCase()}
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${getStageProgress()}%` }}
              />
            </div>
          </div>

          <div className="status-card">
            <h3>Traffic Distribution</h3>
            <div className="traffic-chart">
              <div className="traffic-bar">
                <div
                  className="traffic-canary"
                  style={{ width: `${deploymentStatus.traffic_percentage}%` }}
                >
                  <span>{deploymentStatus.traffic_percentage}%</span>
                </div>
                <div
                  className="traffic-stable"
                  style={{ width: `${100 - deploymentStatus.traffic_percentage}%` }}
                >
                  <span>{100 - deploymentStatus.traffic_percentage}%</span>
                </div>
              </div>
              <div className="traffic-labels">
                <span>Canary</span>
                <span>Stable</span>
              </div>
            </div>
          </div>

          <div className="status-card">
            <h3>Health Metrics</h3>
            <div className="metrics-grid">
              <div className="metric">
                <span className="metric-label">Canary Health</span>
                <span
                  className="metric-value"
                  style={{ color: getHealthColor(deploymentStatus.canary_health) }}
                >
                  {deploymentStatus.canary_health.toFixed(1)}%
                </span>
              </div>
              <div className="metric">
                <span className="metric-label">Error Rate</span>
                <span className="metric-value">
                  {deploymentStatus.error_rate.toFixed(2)}%
                </span>
              </div>
              <div className="metric">
                <span className="metric-label">Latency</span>
                <span className="metric-value">
                  {deploymentStatus.latency_ms.toFixed(0)}ms
                </span>
              </div>
            </div>
          </div>

          <div className="status-card">
            <h3>Deployment Info</h3>
            <div className="info-list">
              <div className="info-item">
                <span className="info-label">Status:</span>
                <span className={`info-value status-${deploymentStatus.status}`}>
                  {deploymentStatus.status}
                </span>
              </div>
              <div className="info-item">
                <span className="info-label">Started:</span>
                <span className="info-value">
                  {new Date(deploymentStatus.start_time).toLocaleString()}
                </span>
              </div>
              {deploymentStatus.end_time && (
                <div className="info-item">
                  <span className="info-label">Completed:</span>
                  <span className="info-value">
                    {new Date(deploymentStatus.end_time).toLocaleString()}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="events-panel">
        <h3>📋 Deployment Events</h3>
        <div className="events-list">
          {events.length === 0 ? (
            <div className="no-events">No events yet. Start a deployment to see real-time updates.</div>
          ) : (
            events.map((event, index) => (
              <div key={index} className={`event-item event-${event.type}`}>
                <span className="event-timestamp">{event.timestamp}</span>
                <span className="event-message">{event.message}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default CanaryDashboard;

// Made with Bob
