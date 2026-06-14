import React, { useState, useEffect } from 'react';
import Papa from 'papaparse';
import { Settings, BarChart2, Users, FileBarChart, PlayCircle, Search, HelpCircle, Activity, Upload, AlertTriangle, BookOpen, Lightbulb, Database, Download, LogOut } from 'lucide-react';
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';
import Plot from 'react-plotly.js';
import LoginPage from './LoginPage';
import './index.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  // ── Auth (must be first hook) ──
  const [currentUser, setCurrentUser] = useState(() => {
    try {
      const saved = sessionStorage.getItem('pc_auth');
      return saved ? JSON.parse(saved).user : null;
    } catch { return null; }
  });

  // ── All other state (hooks must all be called unconditionally) ──
  const [activeTab, setActiveTab]         = useState('dashboard');
  const [report, setReport]               = useState(null);
  const [crowdData, setCrowdData]         = useState([]);
  const [loading, setLoading]             = useState(false);
  const [error, setError]                 = useState(null);
  const [useGemini, setUseGemini]         = useState(false);
  const [apiKey, setApiKey]               = useState('');
  const [mcqFile, setMcqFile]             = useState(null);
  const [humanFile, setHumanFile]         = useState(null);
  const [selectedStudent, setSelectedStudent] = useState('');
  const [mcqData, setMcqData]             = useState([]);
  const [comparisonData, setComparisonData] = useState([]);

  // ── Auth handlers ──
  const handleLogin  = (username) => setCurrentUser(username);
  const handleLogout = () => {
    sessionStorage.removeItem('pc_auth');
    setCurrentUser(null);
  };

  // ── Login gate ──
  // We cannot early return here because hooks must be called unconditionally.
  // Instead, we conditionally render below.


  const classifyDomain = (question) => {
    const q = (question || '').toLowerCase();
    if (q.includes('lim_') || q.includes('d/dx') || q.includes('limit') || q.includes('derivative') || q.includes('integrate') || q.includes('integral')) {
      return 'Calculus';
    } else if (q.includes('z =') || q.includes('|z|') || q.includes('complex') || q.includes('1i') || q.includes('conjugate')) {
      return 'Complex Numbers';
    } else if (q.includes('x^2') || q.includes('factorize') || q.includes('expand') || q.includes('solve') || q.includes('equation')) {
      return 'Algebra & Polynomials';
    } else if (q.includes('area') || q.includes('radius') || q.includes('circle') || q.includes('triangle') || q.includes('distance between') || q.includes('angle') || q.includes('geometry')) {
      return 'Geometry';
    } else {
      return 'Arithmetic';
    }
  };

  // Fetch initial report and data
  useEffect(() => {
    // Always load MCQ bank on startup (Item Bank is always visible)
    fetchMcqData();
    fetchReport();
  }, []);

  const fetchMcqData = () => {
    Papa.parse(`${API_BASE_URL}/data/mcq_bank.csv`, {
      download: true,
      header: true,
      dynamicTyping: true,
      delimiter: ';',
      skipEmptyLines: true,
      complete: (results) => {
        const normalized = results.data
          .filter(row => row.Question || row.question)
          .map((row, idx) => ({
            item_id: idx,
            question:          row.Question          || row.question          || '',
            option_a:          row.Choice_A           || row.option_a          || '',
            option_b:          row.Choice_B           || row.option_b          || '',
            option_c:          row.Choice_C           || row.option_c          || '',
            option_d:          row.Choice_D           || row.option_d          || '',
            correct_option:   (row.Correct_Answer     || row.correct_option    || '').trim().toUpperCase(),
            difficulty_expert: (row.Difficulty        || row.difficulty_expert || 'medium').trim().toLowerCase(),
            domain: classifyDomain(row.Question || row.question || ''),
          }));
        setMcqData(normalized);
      }
    });
  };

  const fetchReport = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/report`);
      if (res.ok) {
        const data = await res.json();
        setReport(data);
        fetchDatasets();
      }
    } catch (err) {
      console.log("No existing report found or API down");
    }
  };

  const fetchDatasets = () => {
    Papa.parse(`${API_BASE_URL}/outputs/response_matrix.csv`, {
      download: true, header: true, dynamicTyping: true,
      complete: (results) => setCrowdData(results.data)
    });
    // Re-load MCQ bank (also triggered on startup via fetchMcqData)
    fetchMcqData();
    Papa.parse(`${API_BASE_URL}/outputs/rasch_comparison.csv`, {
      download: true, header: true, dynamicTyping: true,
      complete: (results) => setComparisonData(results.data)
    });
  };


  const handleRunPipeline = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      // Upload files first if provided
      if (mcqFile) {
        const fd = new FormData(); fd.append('file_type', 'mcq'); fd.append('file', mcqFile);
        await fetch(`${API_BASE_URL}/api/upload`, { method: 'POST', body: fd });
      }
      if (humanFile) {
        const fd = new FormData(); fd.append('file_type', 'human'); fd.append('file', humanFile);
        await fetch(`${API_BASE_URL}/api/upload`, { method: 'POST', body: fd });
      }

      const formData = new FormData();
      formData.append('use_gemini', useGemini);
      if (apiKey) formData.append('api_key', apiKey);

      const res = await fetch(`${API_BASE_URL}/api/run-pipeline`, {
        method: 'POST',
        body: formData,
      });
      
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Pipeline failed');
      
      setReport(data.report);
      fetchDatasets();
      setActiveTab('rasch');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Extract unique students
  const studentIds = [...new Set(crowdData.map(d => d.student_id).filter(Boolean))];

  if (!currentUser) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <div className="app-container">
      {/* Sidebar Premium */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo-icon-flex">
            <span className="integral">∫</span>
            <span className="x">x</span>
            <div className="separator"></div>
            <div className="brand-text">
              <h1>PSYCHOCROWD</h1>
              <p>DECIPHER CROWDS, ANTICIPATE TRENDS</p>
            </div>
          </div>
        </div>
        
        <nav className="main-nav">
          <div className="nav-group">
            <div className="nav-label">Core</div>
            <div className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>
              <Settings size={18} /> Configuration
            </div>
            <div className={`nav-item ${activeTab === 'item_bank' ? 'active' : ''}`} onClick={() => setActiveTab('item_bank')}>
              <Database size={18} /> Item Bank
            </div>
          </div>

          <div className="nav-group">
            <div className="nav-label">Analysis</div>
            <div className={`nav-item ${activeTab === 'crowd' ? 'active' : ''}`} onClick={() => setActiveTab('crowd')}>
              <Users size={18} /> Artificial Crowd
            </div>
            <div className={`nav-item ${activeTab === 'insights' ? 'active' : ''}`} onClick={() => setActiveTab('insights')}>
              <Lightbulb size={18} /> AI Insights
            </div>
            <div className={`nav-item ${activeTab === 'rasch' ? 'active' : ''}`} onClick={() => setActiveTab('rasch')}>
              <Activity size={18} /> Rasch Model
            </div>
            <div className={`nav-item ${activeTab === 'validation' ? 'active' : ''}`} onClick={() => setActiveTab('validation')}>
              <BarChart2 size={18} /> Validation
            </div>
            <div className={`nav-item ${activeTab === 'student' ? 'active' : ''}`} onClick={() => setActiveTab('student')}>
              <Search size={18} /> Student Lookup
            </div>
          </div>

          <div className="nav-group" style={{marginTop: 'auto'}}>
            <div className={`nav-item ${activeTab === 'help' ? 'active' : ''}`} onClick={() => setActiveTab('help')}>
              <HelpCircle size={18} /> Help Center
            </div>
          </div>

          {/* Logout */}
          <div className="sidebar-logout">
            <div className="sidebar-user">Connecté : <span>{currentUser}</span></div>
            <button className="logout-btn" onClick={handleLogout}>
              <LogOut size={15} /> Déconnexion
            </button>
          </div>
        </nav>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        
        {/* TAB: DASHBOARD / CONFIG */}
        {activeTab === 'dashboard' && (
          <div className="fade-in">
            <div className="hero-banner">
              <div className="hero-content">
                <h2>AI Psychometric Engine</h2>
                <p>Run your MCQ bank through Google Gemini to generate artificial student crowds and analyze cognitive behavior using the 1PL Rasch Model.</p>
              </div>
            </div>

            <section className="config-card glass-panel">
              <div className="card-header">
                <h3><Settings size={20} /> Engine Setup</h3>
              </div>
              
              {error && <div className="alert-error">{error}</div>}
              
              <form onSubmit={handleRunPipeline} className="form-layout">
                <div className="form-group row-flex">
                  <div className="file-upload-box">
                    <label>📁 MCQ Bank (CSV)</label>
                    <input type="file" accept=".csv" onChange={(e) => setMcqFile(e.target.files[0])} />
                    <p className="help-text">Leave empty to use default</p>
                  </div>
                  <div className="file-upload-box">
                    <label>📁 Human Responses (CSV)</label>
                    <input type="file" accept=".csv" onChange={(e) => setHumanFile(e.target.files[0])} />
                    <p className="help-text">Leave empty to use default</p>
                  </div>
                </div>

                <div className="form-group row-flex" style={{marginTop: '1.5rem'}}>
                  <div className="toggle-switch">
                    <input 
                      type="checkbox" 
                      id="gemini-toggle"
                      checked={useGemini}
                      onChange={(e) => setUseGemini(e.target.checked)}
                    />
                    <label htmlFor="gemini-toggle">Enable Google Gemini API</label>
                  </div>
                  <p className="help-text">Uses AI to estimate item difficulty. Otherwise falls back to Mock engine.</p>
                </div>
                
                <div className={`form-group ${!useGemini ? 'disabled' : ''}`}>
                  <label>Gemini API Key</label>
                  <input 
                    type="password" 
                    className="form-control premium-input" 
                    placeholder="AIzaSy..."
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    disabled={!useGemini}
                  />
                </div>
                
                <button type="submit" className="btn btn-primary btn-large" disabled={loading}>
                  {loading ? <span className="spinner"></span> : <PlayCircle size={20} />}
                  {loading ? 'Running Simulation...' : 'Launch Simulation'}
                </button>
              </form>
            </section>
          </div>
        )}

        {/* NOT RUN YET STATE FOR OTHER TABS */}
        {activeTab !== 'dashboard' && !report && !loading && (
           <div className="empty-state">
              <Activity size={48} color="#722F37" />
              <h3>No Results Available</h3>
              <p>Please run the simulation from the Configuration tab first.</p>
           </div>
        )}

        {/* LOADING STATE */}
        {loading && (
          <div className="empty-state">
             <div className="spinner large"></div>
             <h3>Processing Engine Pipeline...</h3>
             <p>This usually takes 1-2 minutes depending on the MCQ bank size.</p>
          </div>
        )}

        {/* TAB: ITEM BANK */}
        {activeTab === 'item_bank' && (
          <div className="fade-in">
            <header className="page-header">
              <h2>📚 Item Bank Overview</h2>
              <p>Overview of the generated or uploaded MCQ database.</p>
            </header>

            {mcqData.length === 0 ? (
              <div className="empty-state">
                <Database size={48} color="#94A3B8" />
                <h3>No Items Loaded</h3>
                <p>Run the simulation or upload an MCQ Bank CSV first.</p>
              </div>
            ) : (
              <>
                <div className="stats-grid">
                  <div className="stat-box highlight-box">
                    <div className="stat-title">Total Items</div>
                    <div className="stat-value text-primary">{mcqData.length}</div>
                  </div>
                  <div className="stat-box" style={{borderColor: '#10B981'}}>
                    <div className="stat-title">Easy Items</div>
                    <div className="stat-value" style={{color: '#10B981'}}>
                      {mcqData.filter(d => d.difficulty_expert === 'easy').length}
                    </div>
                  </div>
                  <div className="stat-box" style={{borderColor: '#F59E0B'}}>
                    <div className="stat-title">Medium Items</div>
                    <div className="stat-value" style={{color: '#F59E0B'}}>
                      {mcqData.filter(d => d.difficulty_expert === 'medium').length}
                    </div>
                  </div>
                  <div className="stat-box" style={{borderColor: '#EF4444'}}>
                    <div className="stat-title">Hard Items</div>
                    <div className="stat-value" style={{color: '#EF4444'}}>
                      {mcqData.filter(d => d.difficulty_expert === 'hard').length}
                    </div>
                  </div>
                </div>

                <div className="charts-row" style={{marginBottom: '2rem'}}>
                  <div className="chart-panel half">
                    <h3>Difficulty Distribution</h3>
                    <div style={{height: 250, display: 'flex', justifyContent: 'center'}}>
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={[
                              {name: 'Easy',   value: mcqData.filter(d => d.difficulty_expert === 'easy').length,   fill: '#10B981'},
                              {name: 'Medium', value: mcqData.filter(d => d.difficulty_expert === 'medium').length, fill: '#F59E0B'},
                              {name: 'Hard',   value: mcqData.filter(d => d.difficulty_expert === 'hard').length,   fill: '#EF4444'}
                            ].filter(d => d.value > 0)}
                            cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={5} dataKey="value"
                            label={({name, percent}) => `${name} ${(percent*100).toFixed(0)}%`}
                          >
                            {['#10B981','#F59E0B','#EF4444'].map((color, index) => (
                              <Cell key={index} fill={color} />
                            ))}
                          </Pie>
                          <RechartsTooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                  <div className="chart-panel half">
                    <h3>Distribution by Domain</h3>
                    <div style={{height: 250}}>
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={Object.entries(
                            mcqData.reduce((acc, item) => {
                              const d = item.domain || 'Arithmetic';
                              acc[d] = (acc[d] || 0) + 1;
                              return acc;
                            }, {})
                          ).map(([name, value]) => ({ name, value }))}
                          layout="vertical" margin={{ top: 5, right: 20, left: 80, bottom: 5 }}
                        >
                          <XAxis type="number" />
                          <YAxis dataKey="name" type="category" width={80} tick={{fontSize: 11}} />
                          <RechartsTooltip />
                          <Bar dataKey="value" fill="#722F37" radius={[0, 4, 4, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>

                <div className="data-table-container">
                  <h3 style={{marginBottom: '1rem'}}>Item Preview</h3>
                  <table className="premium-table">
                    <thead>
                      <tr>
                        <th>#</th>
                        <th>Question</th>
                        <th>Domain</th>
                        <th>Difficulty</th>
                        <th>Correct</th>
                      </tr>
                    </thead>
                    <tbody>
                      {mcqData.slice(0, 20).map((row, i) => (
                        <tr key={i}>
                          <td style={{color: 'var(--text-muted)', fontSize: '0.85rem'}}>{row.item_id}</td>
                          <td style={{maxWidth: '300px', fontSize: '0.9rem'}}>{row.question}</td>
                          <td><span className="badge" style={{background: '#EEF2FF', color: '#3730A3', fontSize: '0.75rem'}}>{row.domain}</span></td>
                          <td>
                            <span className={`badge ${
                              row.difficulty_expert === 'easy'   ? 'badge-success' :
                              row.difficulty_expert === 'hard'   ? 'badge-error'   : ''
                            }`} style={row.difficulty_expert === 'medium' ? {background: '#FEF3C7', color: '#B45309'} : {}}>
                              {row.difficulty_expert}
                            </span>
                          </td>
                          <td style={{fontWeight: 600, color: '#059669'}}>Option {row.correct_option}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {mcqData.length > 20 && (
                    <div style={{textAlign: 'center', padding: '1rem', color: 'var(--text-muted)'}}>
                      Showing 20 of {mcqData.length} items
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        )}

        {/* TAB: AI INSIGHTS */}
        {activeTab === 'insights' && report && (
          <div className="fade-in">
            <header className="page-header">
              <h2>AI Insights & Diagnostics</h2>
              <p>Qualitative analysis generated by the Gemini language model.</p>
            </header>

            {report.context_summary && report.context_summary !== "Mock data context." && (
              <div className="glass-panel" style={{marginBottom: '2rem', borderLeft: '4px solid #722F37'}}>
                <h3 style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem'}}>
                  <BookOpen size={20} /> Content Context
                </h3>
                <p style={{fontSize: '1.05rem', lineHeight: 1.6, color: '#334155'}}>{report.context_summary}</p>
              </div>
            )}

            {report.ai_recommendations && report.ai_recommendations.length > 0 ? (
              <div>
                <h3 style={{marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '8px'}}>
                  <Lightbulb size={24} color="#F59E0B"/> Common Mistakes & Recommendations
                </h3>
                {report.ai_recommendations.map((rec, i) => {
                  const accColor = rec.accuracy < 0.3 ? '#EF4444' : (rec.accuracy < 0.6 ? '#F59E0B' : '#10B981');
                  return (
                    <div key={i} className="risk-card" style={{borderLeftColor: accColor, marginBottom: '1rem'}}>
                      <div className="risk-header">
                        <span className="risk-domain" style={{color: '#1E293B', fontSize: '1rem'}}>Item {rec.item_id}</span>
                        <span className="badge" style={{background: `${accColor}15`, color: accColor}}>{(rec.accuracy * 100).toFixed(0)}% Success Rate</span>
                      </div>
                      <p className="risk-q"><b>📝</b> {rec.question}</p>
                      <p style={{marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '1rem'}}>
                        <span style={{color: '#10B981', fontWeight: 600}}>✓ Expected: {rec.correct}</span>
                        <span style={{color: '#EF4444', fontWeight: 600}}>✗ Mistake: {rec.common_mistake}</span>
                      </p>
                      <div className="risk-remedy" style={{background: 'linear-gradient(135deg, #EEF2FF, #F0F9FF)'}}>
                        💡 <b>Remediation:</b> {rec.ai_recommendation}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="empty-state">
                <Lightbulb size={48} color="#94A3B8" />
                <h3>No AI Recommendations</h3>
                <p>Ensure Gemini is enabled and run the simulation to generate pedagogical recommendations.</p>
              </div>
            )}
          </div>
        )}

        {/* TAB: ARTIFICIAL CROWD */}
        {activeTab === 'crowd' && report && crowdData.length > 0 && (() => {
          const profilesList = [...new Set(crowdData.map(d => d.profile).filter(Boolean))].sort();
          const profileColors = { expert: "#2563EB", good: "#10B981", medium: "#F59E0B", weak: "#EF4444" };
          
          const sampleStudents = [...new Set(crowdData.map(d => d.student_id))].slice(0, 40);
          const sampleItems = [...new Set(crowdData.map(d => d.item_id))].sort((a,b)=>a-b).slice(0, 40);
          
          const heatmapZ = [];
          for (let s of sampleStudents) {
            const row = [];
            for (let i of sampleItems) {
              const record = crowdData.find(d => d.student_id === s && d.item_id === i);
              row.push(record ? record.is_correct : 0);
            }
            heatmapZ.push(row);
          }

          const accData = profilesList.map(p => {
            const pData = crowdData.filter(d => d.profile === p);
            return {
              profile: p.toUpperCase(),
              acc: pData.reduce((s, d) => s + (d.is_correct||0), 0) / pData.length
            };
          });

          return (
            <div className="fade-in">
              <header className="page-header">
                <h2>Synthetic Crowd Analysis</h2>
                <p>Simulated mathematical behavior mapped via Gemini responses.</p>
              </header>

              <div className="stats-grid">
                {profilesList.map(p => {
                  const pData = crowdData.filter(d => d.profile === p);
                  const acc = pData.reduce((s, d) => s + (d.is_correct||0), 0) / pData.length;
                  const color = profileColors[p.toLowerCase()] || "#64748B";
                  return (
                    <div key={p} className="stat-box" style={{borderTop: `3px solid ${color}`}}>
                      <div className="stat-title">{p.toUpperCase()}</div>
                      <div className="stat-value" style={{color}}>{(acc*100).toFixed(0)}%</div>
                      <div className="stat-title" style={{marginTop: '4px'}}>accuracy</div>
                    </div>
                  );
                })}
              </div>

              <div className="charts-row">
                <div className="chart-panel half">
                  <h3>Response Matrix (Heatmap)</h3>
                  <Plot
                    data={[{ z: heatmapZ, type: 'heatmap', colorscale: [[0, '#FCA5A5'], [1, '#34D399']], showscale: false }]}
                    layout={{ margin: { t: 10, l: 0, r: 0, b: 0 }, height: 300, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)' }}
                    config={{ displayModeBar: false }}
                    style={{ width: '100%', height: '300px' }}
                  />
                </div>
                <div className="chart-panel half">
                  <h3>Mean Accuracy by Profile</h3>
                  <Plot
                    data={[{
                      x: accData.map(d => d.profile),
                      y: accData.map(d => d.acc),
                      type: 'bar',
                      marker: { color: accData.map(d => profileColors[d.profile.toLowerCase()]) }
                    }]}
                    layout={{ margin: { t: 10, l: 40, r: 10, b: 30 }, height: 300, yaxis: { title: 'Accuracy' }, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)' }}
                    config={{ displayModeBar: false }}
                    style={{ width: '100%', height: '300px' }}
                  />
                </div>
              </div>
            </div>
          );
        })()}

        {/* TAB: RASCH */}
        {activeTab === 'rasch' && report && (
          <div className="fade-in">
            <header className="page-header">
              <h2>Item Response Theory (1PL Rasch)</h2>
              <p>Comparing human vs artificial cognitive abilities.</p>
            </header>

            <div className="metrics-grid">
              <div className="metric-card highlight-left-red">
                <div className="metric-header">🙋‍♂️ Human Students</div>
                <table style={{width:'100%', borderCollapse: 'collapse'}}>
                  <tbody>
                    <tr><td style={{padding:'6px 0', color:'#64748B'}}>Converged</td><td style={{textAlign:'right', fontWeight:600}}>{report.human_rasch.converged ? '✅' : '❌'}</td></tr>
                    <tr><td style={{padding:'6px 0', color:'#64748B'}}>Iterations</td><td style={{textAlign:'right', fontWeight:600}}>{report.human_rasch.n_iterations}</td></tr>
                    <tr><td style={{padding:'6px 0', color:'#64748B'}}>Mean Ability</td><td style={{textAlign:'right', fontWeight:600}}>{report.human_rasch.mean_ability.toFixed(3)} logits</td></tr>
                    <tr><td style={{padding:'6px 0', color:'#64748B'}}>Std Dev Ability</td><td style={{textAlign:'right', fontWeight:600}}>{report.human_rasch.std_ability.toFixed(3)}</td></tr>
                    <tr><td style={{padding:'6px 0', color:'#64748B'}}>Mean Difficulty</td><td style={{textAlign:'right', fontWeight:600}}>{report.human_rasch.mean_difficulty.toFixed(3)} logits</td></tr>
                    <tr><td style={{padding:'6px 0', color:'#64748B'}}>Std Dev Diff</td><td style={{textAlign:'right', fontWeight:600}}>{report.human_rasch.std_difficulty.toFixed(3)}</td></tr>
                  </tbody>
                </table>
              </div>
              <div className="metric-card highlight-left-blue">
                <div className="metric-header">🤖 Artificial Crowd</div>
                <table style={{width:'100%', borderCollapse: 'collapse'}}>
                  <tbody>
                    <tr><td style={{padding:'6px 0', color:'#64748B'}}>Converged</td><td style={{textAlign:'right', fontWeight:600}}>{report.art_rasch.converged ? '✅' : '❌'}</td></tr>
                    <tr><td style={{padding:'6px 0', color:'#64748B'}}>Iterations</td><td style={{textAlign:'right', fontWeight:600}}>{report.art_rasch.n_iterations}</td></tr>
                    <tr><td style={{padding:'6px 0', color:'#64748B'}}>Mean Ability</td><td style={{textAlign:'right', fontWeight:600}}>{report.art_rasch.mean_ability.toFixed(3)} logits</td></tr>
                    <tr><td style={{padding:'6px 0', color:'#64748B'}}>Std Dev Ability</td><td style={{textAlign:'right', fontWeight:600}}>{report.art_rasch.std_ability.toFixed(3)}</td></tr>
                    <tr><td style={{padding:'6px 0', color:'#64748B'}}>Mean Difficulty</td><td style={{textAlign:'right', fontWeight:600}}>{report.art_rasch.mean_difficulty.toFixed(3)} logits</td></tr>
                    <tr><td style={{padding:'6px 0', color:'#64748B'}}>Std Dev Diff</td><td style={{textAlign:'right', fontWeight:600}}>{report.art_rasch.std_difficulty.toFixed(3)}</td></tr>
                  </tbody>
                </table>
              </div>
            </div>

            <section className="chart-panel">
              <h3>Wright Map (Person-Item Distribution)</h3>
              <img src={`${API_BASE_URL}/outputs/plots/wright_map.png`} alt="Wright Map" className="chart-image" />
            </section>
          </div>
        )}

        {/* TAB: VALIDATION */}
        {activeTab === 'validation' && report && (
          <div className="fade-in">
            <header className="page-header">
              <h2>Psychometric Validation</h2>
              <p>Correlation and errors between AI-generated data and real human data.</p>
            </header>

            <div className="stats-grid">
              <div className="stat-box">
                <div className="stat-title">Pearson r</div>
                <div className="stat-value text-success">{report.comparison.pearson_r.toFixed(4)}</div>
              </div>
              <div className="stat-box">
                <div className="stat-title">Spearman ρ</div>
                <div className="stat-value text-success">{report.comparison.spearman_r.toFixed(4)}</div>
              </div>
              <div className="stat-box">
                <div className="stat-title">Mean Absolute Error</div>
                <div className="stat-value">{report.comparison.mae.toFixed(4)}</div>
              </div>
              <div className="stat-box highlight-box">
                <div className="stat-title">Verdict</div>
                <div className="stat-value text-primary">{report.comparison.interpretation}</div>
              </div>
            </div>

            <div className="charts-row">
              <div className="chart-panel half">
                <h3>Scatter Comparison</h3>
                <img src={`${API_BASE_URL}/outputs/plots/scatter_comparison.png`} alt="Scatter Comparison" className="chart-image" />
              </div>
              <div className="chart-panel half">
                <h3>Difficulty Distribution</h3>
                <img src={`${API_BASE_URL}/outputs/plots/difficulty_distribution.png`} alt="Distribution" className="chart-image" />
              </div>
            </div>

            <div style={{marginTop: '2rem'}}>
              <a 
                href={`data:text/json;charset=utf-8,${encodeURIComponent(JSON.stringify(report, null, 2))}`}
                download="psychocrowd_report.json"
                className="btn btn-primary"
                style={{textDecoration: 'none', display: 'inline-flex'}}
              >
                <Download size={18} /> Download Raw JSON Report
              </a>
            </div>
          </div>
        )}

        {/* TAB: STUDENT LOOKUP */}
        {activeTab === 'student' && report && crowdData.length > 0 && (
          <div className="fade-in">
            <header className="page-header">
              <h2>Student Lookup Engine</h2>
              <p>Analyze individual student performance across the MCQ bank.</p>
            </header>

            <section className="glass-panel lookup-panel">
              <div className="form-group">
                <label>Select a Student ID</label>
                <select 
                  className="form-control premium-select"
                  value={selectedStudent}
                  onChange={(e) => setSelectedStudent(e.target.value)}
                >
                  <option value="">-- Choose a student --</option>
                  {studentIds.map(id => (
                    <option key={id} value={id}>{id}</option>
                  ))}
                </select>
              </div>

              {selectedStudent && (() => {
                const studentData = crowdData.filter(d => d.student_id === selectedStudent);
                const profile = studentData[0]?.profile || 'Unknown';
                const acc = studentData.length ? studentData.reduce((s, d) => s + (d.is_correct || 0), 0) / studentData.length : 0;
                
                // Get Theta
                let theta = 0;
                if (profile === "Human" && report.human_thetas) theta = report.human_thetas[selectedStudent] || 0;
                else if (report.art_thetas) theta = report.art_thetas[selectedStudent] || 0;

                // Make IRT Predictions
                const predictions = mcqData.map(item => {
                  const b_j = comparisonData.find(c => String(c.item_id) === String(item.item_id))?.[profile === "Human" ? "b_human" : "b_artificial"] || 0;
                  const p_success = 1.0 / (1.0 + Math.exp(-(theta - b_j)));
                  
                  return {
                    item_id: item.item_id,
                    question: item.question,
                    correct_option: item.correct_option,
                    difficulty: item.difficulty_expert || 'medium',
                    domain: item.domain || classifyDomain(item.question),
                    prob: p_success
                  };
                });

                const domainStats = Object.entries(
                  predictions.reduce((acc, curr) => {
                    if (!acc[curr.domain]) acc[curr.domain] = { sum: 0, count: 0 };
                    acc[curr.domain].sum += curr.prob;
                    acc[curr.domain].count += 1;
                    return acc;
                  }, {})
                ).map(([name, data]) => ({ name, prob: data.sum / data.count }));

                const risks = [...predictions].sort((a, b) => a.prob - b.prob).slice(0, 5);

                return (
                  <div className="student-details">
                    <div className="metrics-grid" style={{marginTop: '2rem'}}>
                      <div className="metric-card" style={{borderTop: '3px solid #10B981'}}>
                        <div className="stat-title">Actual Accuracy</div>
                        <div className="stat-value" style={{color: '#10B981'}}>{(acc * 100).toFixed(1)}%</div>
                      </div>
                      <div className="metric-card" style={{borderTop: '3px solid #7C3AED'}}>
                        <div className="stat-title">Profile</div>
                        <div className="stat-value" style={{color: '#7C3AED', textTransform: 'capitalize'}}>{profile}</div>
                      </div>
                      <div className="metric-card" style={{borderTop: '3px solid #2563EB'}}>
                        <div className="stat-title">IRT Latent Ability (θ)</div>
                        <div className="stat-value" style={{color: '#2563EB'}}>{theta > 0 ? '+' : ''}{theta.toFixed(3)}</div>
                        <div className="help-text">measured in logits</div>
                      </div>
                    </div>

                    <div className="charts-row" style={{marginTop: '2rem'}}>
                      <div className="chart-panel" style={{width: '100%'}}>
                        <h3>Forecasted Success Rates</h3>
                        <div style={{display: 'flex', gap: '1rem', marginBottom: '1rem'}}>
                          <div className="stat-box" style={{flex: 1, padding: '1rem'}}>
                            <div className="stat-title">Taux Faciles Prédit</div>
                            <div className="stat-value" style={{color: '#10B981'}}>
                              {((predictions.filter(p => p.difficulty?.toLowerCase() === 'easy').reduce((s, c) => s + c.prob, 0) / (predictions.filter(p => p.difficulty?.toLowerCase() === 'easy').length || 1)) * 100).toFixed(0)}%
                            </div>
                          </div>
                          <div className="stat-box" style={{flex: 1, padding: '1rem'}}>
                            <div className="stat-title">Taux Moyens Prédit</div>
                            <div className="stat-value" style={{color: '#F59E0B'}}>
                              {((predictions.filter(p => p.difficulty?.toLowerCase() === 'medium').reduce((s, c) => s + c.prob, 0) / (predictions.filter(p => p.difficulty?.toLowerCase() === 'medium').length || 1)) * 100).toFixed(0)}%
                            </div>
                          </div>
                          <div className="stat-box" style={{flex: 1, padding: '1rem'}}>
                            <div className="stat-title">Taux Difficiles Prédit</div>
                            <div className="stat-value" style={{color: '#EF4444'}}>
                              {((predictions.filter(p => p.difficulty?.toLowerCase() === 'hard').reduce((s, c) => s + c.prob, 0) / (predictions.filter(p => p.difficulty?.toLowerCase() === 'hard').length || 1)) * 100).toFixed(0)}%
                            </div>
                          </div>
                        </div>
                        <div style={{height: 250}}>
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={domainStats} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                              <XAxis type="number" domain={[0, 1]} tickFormatter={(val) => `${(val*100).toFixed(0)}%`} />
                              <YAxis dataKey="name" type="category" width={100} />
                              <RechartsTooltip formatter={(val) => `${(val*100).toFixed(1)}%`} />
                              <Bar dataKey="prob" fill="#10B981" radius={[0, 4, 4, 0]} />
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    </div>

                    <div style={{marginTop: '2rem'}}>
                      <h3 style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1rem'}}>
                        <AlertTriangle color="#EF4444" /> Highest Risk of Failure (Top 5)
                      </h3>
                      <div className="risks-list">
                        {risks.map((r, i) => {
                          const riskColor = r.prob < 0.25 ? '#EF4444' : (r.prob < 0.5 ? '#F59E0B' : '#10B981');
                          let recText = 'Revoir les bases mathématiques associées.';
                          if (r.domain === 'Calculus')              recText = "Étudier les règles de dérivation en cascade et les formules trigonométriques complexes.";
                          else if (r.domain === 'Complex Numbers')   recText = "Revoir la définition du module d'un nombre complexe et les représentations géométriques.";
                          else if (r.domain === 'Algebra & Polynomials') recText = "S'exercer sur la factorisation d'identités remarquables et les équations quadratiques.";
                          else if (r.domain === 'Geometry')          recText = "Retravailler les formules d'aires classiques (cercle, triangles) et la formule de distance d'Euclide.";
                          else if (r.domain === 'Arithmetic')        recText = "Revoir le calcul fractionnaire et les règles de priorités opératoires.";

                          return (
                            <div key={i} className="risk-card" style={{borderLeftColor: riskColor}}>
                              <div className="risk-header">
                                <span className="risk-domain">Domaine : {r.domain} | Difficulté : {r.difficulty}</span>
                                <span className="risk-prob" style={{color: riskColor}}>Probabilité de réussite : {(r.prob * 100).toFixed(0)}%</span>
                              </div>
                              <p className="risk-q"><b>Question :</b> {r.question}</p>
                              {r.correct_option && (
                                <p style={{margin: '0 0 8px', fontSize: '0.85rem', color: '#059669'}}>
                                  <b>Réponse attendue :</b> Option {r.correct_option}
                                </p>
                              )}
                              <div className="risk-remedy">💡 <b>Recommandation de remédiation :</b> {recText}</div>
                            </div>
                          );
                        })}
                      </div>
                    </div>

                    <h3 style={{marginTop: '3rem', marginBottom: '1rem'}}><BookOpen size={20}/> Raw Responses</h3>
                    <div className="data-table-container">
                      <table className="premium-table">
                        <thead>
                          <tr>
                            <th>Item ID</th>
                            <th>Difficulty</th>
                            <th>Correct?</th>
                            <th>Option Chosen</th>
                          </tr>
                        </thead>
                        <tbody>
                          {studentData.map((row, i) => (
                            <tr key={i}>
                              <td>{row.item_id}</td>
                              <td>{row.difficulty_expert || 'Unknown'}</td>
                              <td>
                                <span className={`badge ${row.is_correct === 1 ? 'badge-success' : 'badge-error'}`}>
                                  {row.is_correct === 1 ? 'Correct' : 'Wrong'}
                                </span>
                              </td>
                              <td>{row.chosen_option || '-'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                );
              })()}
            </section>
          </div>
        )}

        {/* TAB: HELP CENTER */}
        {activeTab === 'help' && (
          <div className="fade-in">
            <header className="page-header">
              <h2>Help Center & Tutorial</h2>
              <p>Mastering the PsychoCrowd Engine.</p>
            </header>
            
            <div className="glass-panel" style={{marginBottom: '1.5rem'}}>
              <h3>1. Data Preparation</h3>
              <p>Upload your <strong>MCQ Bank</strong> and (optional) <strong>Human Responses</strong> in the Configuration tab. Leave blank to auto-generate mock datasets.</p>
            </div>
            
            <div className="glass-panel" style={{marginBottom: '1.5rem'}}>
              <h3>2. Engine Configuration</h3>
              <p>Enable the <strong>Google Gemini API</strong> for AI-driven psychometrics. Responses are cached locally to save API quota on subsequent runs.</p>
            </div>
            
            <div className="glass-panel" style={{marginBottom: '1.5rem'}}>
              <h3>3. Rasch Analysis (IRT)</h3>
              <p>The 1PL model calculates Latent Ability (θ) and Item Difficulty (b). Use the <strong>Wright Map</strong> to visualize alignment between students and questions.</p>
            </div>
            
            <div className="glass-panel">
              <h3>4. Predictive Forecasting</h3>
              <p>In the <strong>Student Lookup</strong> tab, the engine predicts future success rates across domains using the logistic IRT formula: <code>P = 1 / (1 + exp(-(θ - b)))</code>, and identifies the highest risk areas for failure.</p>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}

export default App;
