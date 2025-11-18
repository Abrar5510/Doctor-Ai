import { useState, useEffect } from 'react'
import axios from 'axios'
import '../styles/Dashboard.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function Dashboard() {
  const [overview, setOverview] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [cases, setCases] = useState([])
  const [conditionAnalytics, setConditionAnalytics] = useState(null)
  const [timeline, setTimeline] = useState(null)
  const [demographics, setDemographics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [selectedTab, setSelectedTab] = useState('overview')

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      const [overviewRes, metricsRes, casesRes, conditionsRes, timelineRes, demoRes] = await Promise.all([
        axios.get(`${API_URL}/api/v1/dashboard/overview`),
        axios.get(`${API_URL}/api/v1/dashboard/metrics?days=14`),
        axios.get(`${API_URL}/api/v1/dashboard/cases?limit=10`),
        axios.get(`${API_URL}/api/v1/dashboard/analytics/conditions`),
        axios.get(`${API_URL}/api/v1/dashboard/analytics/timeline`),
        axios.get(`${API_URL}/api/v1/dashboard/analytics/demographics`)
      ])

      setOverview(overviewRes.data)
      setMetrics(metricsRes.data)
      setCases(casesRes.data.cases)
      setConditionAnalytics(conditionsRes.data)
      setTimeline(timelineRes.data)
      setDemographics(demoRes.data)
    } catch (error) {
      console.error('Error fetching dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>Loading Dashboard...</p>
      </div>
    )
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>🏥 Doctor AI - Admin Dashboard</h1>
        <p className="dashboard-subtitle">AI-Powered Medical Diagnosis System Analytics</p>
      </div>

      <div className="dashboard-tabs">
        <button
          className={selectedTab === 'overview' ? 'tab active' : 'tab'}
          onClick={() => setSelectedTab('overview')}
        >
          📊 Overview
        </button>
        <button
          className={selectedTab === 'cases' ? 'tab active' : 'tab'}
          onClick={() => setSelectedTab('cases')}
        >
          📋 Recent Cases
        </button>
        <button
          className={selectedTab === 'analytics' ? 'tab active' : 'tab'}
          onClick={() => setSelectedTab('analytics')}
        >
          📈 Analytics
        </button>
        <button
          className={selectedTab === 'performance' ? 'tab active' : 'tab'}
          onClick={() => setSelectedTab('performance')}
        >
          ⚡ Performance
        </button>
      </div>

      <div className="dashboard-content">
        {selectedTab === 'overview' && overview && (
          <div className="overview-section">
            <div className="stats-grid">
              <div className="stat-card primary">
                <div className="stat-icon">🔬</div>
                <div className="stat-info">
                  <h3>{overview.total_cases}</h3>
                  <p>Total Cases Analyzed</p>
                </div>
              </div>

              <div className="stat-card success">
                <div className="stat-icon">✅</div>
                <div className="stat-info">
                  <h3>{(overview.average_confidence * 100).toFixed(1)}%</h3>
                  <p>Average Confidence</p>
                </div>
              </div>

              <div className="stat-card warning">
                <div className="stat-icon">🚨</div>
                <div className="stat-info">
                  <h3>{overview.red_flags_detected}</h3>
                  <p>Red Flags Detected</p>
                </div>
              </div>

              <div className="stat-card info">
                <div className="stat-icon">📊</div>
                <div className="stat-info">
                  <h3>{overview.total_diagnoses}</h3>
                  <p>Total Diagnoses</p>
                </div>
              </div>
            </div>

            <div className="charts-row">
              <div className="chart-card">
                <h3>Review Tier Distribution</h3>
                <div className="tier-chart">
                  <div className="tier-bar">
                    <div className="tier-label">
                      <span className="tier-badge tier1">Tier 1</span>
                      <span className="tier-desc">&gt;85% Confidence</span>
                    </div>
                    <div className="tier-progress">
                      <div
                        className="tier-fill tier1"
                        style={{
                          width: `${(overview.tier_distribution.tier1 / overview.total_cases) * 100}%`
                        }}
                      >
                        <span className="tier-count">{overview.tier_distribution.tier1} cases</span>
                      </div>
                    </div>
                  </div>

                  <div className="tier-bar">
                    <div className="tier-label">
                      <span className="tier-badge tier2">Tier 2</span>
                      <span className="tier-desc">60-85% Confidence</span>
                    </div>
                    <div className="tier-progress">
                      <div
                        className="tier-fill tier2"
                        style={{
                          width: `${(overview.tier_distribution.tier2 / overview.total_cases) * 100}%`
                        }}
                      >
                        <span className="tier-count">{overview.tier_distribution.tier2} cases</span>
                      </div>
                    </div>
                  </div>

                  <div className="tier-bar">
                    <div className="tier-label">
                      <span className="tier-badge tier3">Tier 3</span>
                      <span className="tier-desc">40-60% Confidence</span>
                    </div>
                    <div className="tier-progress">
                      <div
                        className="tier-fill tier3"
                        style={{
                          width: `${(overview.tier_distribution.tier3 / overview.total_cases) * 100}%`
                        }}
                      >
                        <span className="tier-count">{overview.tier_distribution.tier3} cases</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="chart-card">
                <h3>Top 10 Conditions</h3>
                <div className="conditions-list">
                  {overview.top_conditions.slice(0, 10).map((condition, idx) => (
                    <div key={idx} className="condition-item">
                      <span className="condition-rank">#{idx + 1}</span>
                      <span className="condition-name">{condition.name}</span>
                      <span className="condition-count">{condition.count} cases</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {selectedTab === 'cases' && cases && (
          <div className="cases-section">
            <h2>Recent Patient Cases</h2>
            <div className="cases-table-wrapper">
              <table className="cases-table">
                <thead>
                  <tr>
                    <th>Case ID</th>
                    <th>Age/Sex</th>
                    <th>Chief Complaint</th>
                    <th>Symptoms</th>
                    <th>Review Tier</th>
                    <th>Status</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {cases.map((case_, idx) => (
                    <tr key={idx}>
                      <td className="case-id">{case_.case_id}</td>
                      <td>{case_.patient_age}/{case_.patient_sex}</td>
                      <td className="chief-complaint">{case_.chief_complaint}</td>
                      <td className="symptoms-cell">
                        <div className="symptoms-truncated">
                          {case_.symptoms.substring(0, 60)}...
                        </div>
                      </td>
                      <td>
                        <span className={`tier-badge tier${case_.review_tier}`}>
                          Tier {case_.review_tier}
                        </span>
                      </td>
                      <td>
                        <span className="status-badge completed">
                          {case_.status}
                        </span>
                      </td>
                      <td>{new Date(case_.created_at).toLocaleDateString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {selectedTab === 'analytics' && conditionAnalytics && demographics && (
          <div className="analytics-section">
            <div className="analytics-grid">
              <div className="analytics-card">
                <h3>Top Conditions by Frequency</h3>
                <div className="conditions-chart">
                  {conditionAnalytics.conditions.slice(0, 10).map((condition, idx) => (
                    <div key={idx} className="condition-bar-item">
                      <div className="condition-info">
                        <span className="condition-name">{condition.name}</span>
                        <span className="condition-stats">
                          {condition.count} cases · {(condition.avg_confidence * 100).toFixed(1)}% avg confidence
                        </span>
                      </div>
                      <div className="condition-bar-wrapper">
                        <div
                          className="condition-bar-fill"
                          style={{
                            width: `${(condition.count / conditionAnalytics.conditions[0].count) * 100}%`
                          }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="analytics-card">
                <h3>Demographics Overview</h3>
                <div className="demographics-section">
                  <h4>Age Distribution</h4>
                  <div className="demo-chart">
                    {demographics.age_distribution.map((group, idx) => (
                      <div key={idx} className="demo-item">
                        <span className="demo-label">{group.group}</span>
                        <div className="demo-bar">
                          <div
                            className="demo-bar-fill"
                            style={{
                              width: `${(group.count / cases.length) * 100}%`
                            }}
                          ></div>
                          <span className="demo-count">{group.count}</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  <h4>Gender Distribution</h4>
                  <div className="demo-chart">
                    {demographics.gender_distribution.map((gender, idx) => (
                      <div key={idx} className="demo-item">
                        <span className="demo-label">{gender.gender === 'M' ? 'Male' : gender.gender === 'F' ? 'Female' : 'Other'}</span>
                        <div className="demo-bar">
                          <div
                            className="demo-bar-fill"
                            style={{
                              width: `${(gender.count / cases.length) * 100}%`
                            }}
                          ></div>
                          <span className="demo-count">{gender.count}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {selectedTab === 'performance' && metrics && (
          <div className="performance-section">
            <div className="perf-stats-grid">
              <div className="perf-stat-card">
                <h4>Average Response Time</h4>
                <div className="perf-value">{metrics.aggregated_stats.average_response_time_ms.toFixed(0)} ms</div>
                <div className="perf-trend positive">▲ Optimal</div>
              </div>

              <div className="perf-stat-card">
                <h4>Cache Hit Rate</h4>
                <div className="perf-value">{(metrics.aggregated_stats.average_cache_hit_rate * 100).toFixed(1)}%</div>
                <div className="perf-trend positive">▲ Excellent</div>
              </div>

              <div className="perf-stat-card">
                <h4>System Uptime</h4>
                <div className="perf-value">{metrics.aggregated_stats.average_uptime_percentage.toFixed(2)}%</div>
                <div className="perf-trend positive">▲ Excellent</div>
              </div>

              <div className="perf-stat-card">
                <h4>Total Cases Analyzed</h4>
                <div className="perf-value">{metrics.aggregated_stats.total_cases_analyzed}</div>
                <div className="perf-trend positive">Last {metrics.period_days} days</div>
              </div>
            </div>

            <div className="metrics-timeline">
              <h3>Performance Metrics Over Time</h3>
              <div className="timeline-table-wrapper">
                <table className="metrics-table">
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>Cases</th>
                      <th>Avg Confidence</th>
                      <th>Response Time</th>
                      <th>Cache Hit Rate</th>
                      <th>Red Flags</th>
                      <th>Uptime</th>
                    </tr>
                  </thead>
                  <tbody>
                    {metrics.metrics_data.map((metric, idx) => (
                      <tr key={idx}>
                        <td>{metric.metric_date}</td>
                        <td>{metric.total_cases_analyzed}</td>
                        <td>{(metric.avg_confidence_score * 100).toFixed(1)}%</td>
                        <td>{metric.avg_response_time_ms} ms</td>
                        <td>{(metric.cache_hit_rate * 100).toFixed(1)}%</td>
                        <td>{metric.red_flags_detected}</td>
                        <td className="uptime-cell">
                          <span className={metric.uptime_percentage >= 99.9 ? 'uptime-good' : 'uptime-warning'}>
                            {metric.uptime_percentage}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Dashboard
