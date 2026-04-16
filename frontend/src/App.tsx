const formatNumber = (value: any, digits = 2): string => {
  const num = Number(value);
  return isNaN(num) ? "0.00" : num.toFixed(digits);
};
import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar
} from 'recharts';
import { 
  TrendingUp, TrendingDown, Users, Target, Award, 
  BarChart3, PieChart as PieChartIcon, History, PlayCircle, RotateCcw,
  LogOut, Shield, ChevronRight, LayoutDashboard, Trophy, Settings
} from 'lucide-react';
import { simulationApi } from './services/api';
import { useAuthStore } from './store/useAuthStore';
import { ProtectedRoute } from './components/ProtectedRoute';

const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#6366f1'];

// --- Dashboard Component ---
const Dashboard: React.FC = () => {
  const { user, logout } = useAuthStore();
  const [state, setState] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [leaderboard, setLeaderboard] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [amount, setAmount] = useState(5000);
  const [selectedTask, setSelectedTask] = useState('grow_market_share');
  const [selectedDifficulty, setSelectedDifficulty] = useState('medium');
  const navigate = useNavigate();

  const fetchData = async () => {
    try {
      const [stateRes, historyRes, leaderboardRes] = await Promise.all([
        simulationApi.getState(),
        simulationApi.getHistory(),
        simulationApi.getLeaderboard()
      ]);
      setState(stateRes.data);
      setHistory(historyRes.data.history);
      setLeaderboard(leaderboardRes.data.leaderboard);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleStep = async (action: string) => {
    try {
      const res = await simulationApi.step(action, amount);
      setState(res.data);
      const histRes = await simulationApi.getHistory();
      setHistory(histRes.data.history);
    } catch (error) {
      console.error('Error taking step:', error);
    }
  };

  const handleReset = async () => {
    try {
      const res = await simulationApi.reset(selectedTask, selectedDifficulty, Math.floor(Math.random() * 10000));
      setState(res.data);
      setHistory([]);
      const leaderRes = await simulationApi.getLeaderboard();
      setLeaderboard(leaderRes.data.leaderboard);
    } catch (error) {
      console.error('Error resetting:', error);
    }
  };

  if (!state) return (
    <div className="flex items-center justify-center h-screen bg-slate-900 text-blue-400 font-mono">
      <div className="flex flex-col items-center gap-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        <div className="animate-pulse">SYNCHRONIZING ENTERPRISE TERMINAL...</div>
      </div>
    </div>
  );

  const chartData = state.chart_revenue.map((rev: number, i: number) => ({
    name: `Q${i}`,
    revenue: rev,
    profit: state.chart_profit[i]
  }));

  const pieData = [
    { name: 'You', value: state.market_share * 100 },
    ...state.competitors.map((c: any) => ({ name: c.name, value: c.market_share * 100 })),
    { name: 'Other', value: Math.max(0, 100 - (state.market_share * 100) - state.competitors.reduce((acc: number, c: any) => acc + c.market_share * 100, 0)) }
  ];

  const barData = [
    {
      name: 'Market Share %',
      You: state.market_share * 100,
      RivalCorp: state.competitors[0]?.market_share * 100 || 0,
      MegaCo: state.competitors[1]?.market_share * 100 || 0,
    },
    {
      name: 'Satisfaction',
      You: state.customer_satisfaction * 100,
      RivalCorp: 60,
      MegaCo: 75,
    },
    {
      name: 'Quality',
      You: state.product_quality * 100,
      RivalCorp: 60,
      MegaCo: 70,
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans antialiased">
      {/* Top Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between sticky top-0 z-50 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="bg-blue-600 text-white p-2 rounded-xl shadow-lg shadow-blue-100">
            <LayoutDashboard size={24} />
          </div>
          <div>
            <h1 className="text-xl font-extrabold tracking-tight text-slate-900">
              BizSim <span className="text-blue-600">Pro</span>
            </h1>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center gap-1">
              <Shield size={10} /> Enterprise Tier
            </div>
          </div>
        </div>
        
        <div className="flex-1 mx-12 hidden lg:block">
          <div className="bg-slate-100 rounded-full px-6 py-2.5 flex items-center gap-4 overflow-hidden border border-slate-200/50">
             <span className="text-[10px] font-black text-blue-600 uppercase tracking-tighter whitespace-nowrap bg-blue-100 px-2 py-0.5 rounded">Real-time Feed</span>
             <div className="text-sm text-slate-600 font-medium animate-in slide-in-from-right-full duration-1000">
               {state.news || "Stable market conditions reported across all sectors."}
             </div>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5">
            <RotateCcw size={14} className="text-blue-500" />
            <span className="text-sm font-bold text-slate-700">Q{state.quarter} <span className="text-slate-300 mx-1">/</span> {state.max_quarters}</span>
          </div>
          <div className="flex items-center gap-3 pl-6 border-l border-slate-200">
            <div className="text-right">
              <div className="text-xs font-bold text-slate-900">{user?.full_name || user?.email}</div>
              <div className="text-[10px] font-bold text-emerald-500 uppercase tracking-wider">Online</div>
            </div>
            <button 
              onClick={() => { logout(); navigate('/login'); }}
              className="p-2 text-slate-400 hover:text-rose-500 hover:bg-rose-50 rounded-full transition-all"
            >
              <LogOut size={20} />
            </button>
          </div>
        </div>
      </header>

      <main className="grid grid-cols-12 gap-6 p-6 max-w-[1600px] mx-auto">
        {/* Sidebar Controls */}
        <div className="col-span-12 lg:col-span-3 space-y-6">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xs font-black text-slate-400 uppercase tracking-widest">Financial Summary</h2>
              <div className={`text-xs font-bold px-2 py-1 rounded ${state.profit >= 0 ? 'bg-emerald-50 text-emerald-600' : 'bg-rose-50 text-rose-600'}`}>
                {state.profit >= 0 ? '+' : ''}{formatNumber((state.profit / state.revenue) * 100)}% Margin
              </div>
            </div>
            <div className="grid grid-cols-1 gap-4">
              <StatCard label="Total Revenue" value={`$${state.revenue.toLocaleString()}`} icon={<TrendingUp size={16} />} color="blue" />
              <StatCard label="Net Profit" value={`$${state.profit.toLocaleString()}`} icon={<Award size={16} />} color={state.profit >= 0 ? "emerald" : "rose"} />
              <StatCard label="Market Share" value={`${formatNumber(state.market_share * 100)}%`} icon={<PieChartIcon size={16} />} color="indigo" />
            </div>
            <div className="mt-6 pt-6 border-t border-slate-100 grid grid-cols-3 gap-2">
              <MiniStat label="Staff" value={state.employees} />
              <MiniStat label="CSAT" value={`${formatNumber(state.customer_satisfaction * 100)}%`} />
              <MiniStat label="Quality" value={`${formatNumber(state.product_quality * 100)}%`} />
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <h2 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-6">Strategic Terminal</h2>
            <div className="space-y-5">
              <div>
                <div className="flex justify-between mb-1.5">
                  <label className="text-xs font-bold text-slate-500">Investment Pool</label>
                  <span className="text-xs font-black text-blue-600">${amount.toLocaleString()}</span>
                </div>
                <input 
                  type="range" 
                  min="500" max="25000" step="500"
                  value={amount} 
                  onChange={(e) => setAmount(Number(e.target.value))}
                  className="w-full h-1.5 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
              </div>
              <div className="grid grid-cols-2 gap-2.5">
                <ActionBtn label="Marketing" onClick={() => handleStep('increase_marketing')} icon="📣" />
                <ActionBtn label="R&D Lab" onClick={() => handleStep('invest_in_rd')} icon="🔬" />
                <ActionBtn label="Expansion" onClick={() => handleStep('expand_market')} icon="🌍" />
                <ActionBtn label="Hiring" onClick={() => handleStep('hire_employees')} icon="👷" />
                <ActionBtn label="Launch" onClick={() => handleStep('launch_product')} icon="🚀" />
                <ActionBtn label="Efficiency" onClick={() => handleStep('cut_costs')} icon="✂️" />
                <ActionBtn label="Raise Price" onClick={() => handleStep('raise_prices')} icon="💰" />
                <ActionBtn label="Lower Price" onClick={() => handleStep('lower_prices')} icon="🏷️" />
              </div>
            </div>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <h2 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-6">Simulation Config</h2>
            <div className="space-y-4">
              <div>
                <label className="text-xs font-bold text-slate-500 mb-1.5 block">Objective</label>
                <select 
                  value={selectedTask}
                  onChange={(e) => setSelectedTask(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm font-medium outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="survive">Survival Protocol (4 Q)</option>
                  <option value="grow_market_share">Aggressive Growth (8 Q)</option>
                  <option value="scale_profitably">Profit Optimization (12 Q)</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-bold text-slate-500 mb-1.5 block">AI Difficulty</label>
                <div className="grid grid-cols-3 gap-2">
                  {['easy', 'medium', 'hard'].map((d) => (
                    <button
                      key={d}
                      onClick={() => setSelectedDifficulty(d)}
                      className={`py-2 text-[10px] font-black uppercase tracking-widest rounded-lg border transition-all ${selectedDifficulty === d ? 'bg-slate-900 border-slate-900 text-white shadow-lg' : 'bg-white border-slate-200 text-slate-400 hover:border-slate-300'}`}
                    >
                      {d}
                    </button>
                  ))}
                </div>
              </div>
              <button 
                onClick={handleReset}
                className="w-full py-3 bg-blue-600 text-white rounded-xl text-sm font-bold hover:bg-blue-700 transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-100 active:scale-[0.98]"
              >
                <RotateCcw size={16} /> Deploy New Simulation
              </button>
            </div>
          </div>
        </div>

        {/* Dashboard Grid */}
        <div className="col-span-12 lg:col-span-9 grid grid-cols-12 gap-6">
          <ChartCard title="Performance Trajectory" icon={<TrendingUp size={18} />} className="col-span-12 lg:col-span-8">
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <defs>
                    <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fontSize: 11, fill: '#94a3b8', fontWeight: 600}} />
                  <YAxis axisLine={false} tickLine={false} tick={{fontSize: 11, fill: '#94a3b8', fontWeight: 600}} />
                  <Tooltip 
                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)', padding: '12px' }} 
                    itemStyle={{ fontWeight: 700, fontSize: '12px' }}
                  />
                  <Legend iconType="circle" wrapperStyle={{ paddingTop: '20px', fontSize: '12px', fontWeight: 600 }} />
                  <Line type="monotone" dataKey="revenue" stroke="#3b82f6" strokeWidth={4} dot={{ r: 0 }} activeDot={{ r: 6, strokeWidth: 0 }} name="Revenue ($)" />
                  <Line type="monotone" dataKey="profit" stroke="#10b981" strokeWidth={4} dot={{ r: 0 }} activeDot={{ r: 6, strokeWidth: 0 }} name="Net Profit ($)" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>

          <ChartCard title="Market Dominance" icon={<PieChartIcon size={18} />} className="col-span-12 lg:col-span-4">
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%" cy="50%"
                    innerRadius={70}
                    outerRadius={95}
                    paddingAngle={8}
                    dataKey="value"
                    stroke="none"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)' }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none mt-6">
                <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">You Hold</span>
                <span className="text-3xl font-black text-slate-900">{formatNumber(state.market_share * 100)}%</span>
              </div>
            </div>
          </ChartCard>

          <div className="col-span-12 lg:col-span-6 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-2 text-slate-800">
                <div className="text-blue-500"><History size={18} /></div>
                <h3 className="font-black text-xs uppercase tracking-widest">Transaction History</h3>
              </div>
              <span className="text-[10px] font-black bg-slate-100 text-slate-500 px-2 py-1 rounded uppercase">{history.length} Events</span>
            </div>
            <div className="overflow-auto h-[350px] pr-2 custom-scrollbar">
              <table className="w-full text-left">
                <thead className="sticky top-0 bg-white text-[10px] font-black text-slate-400 uppercase tracking-tighter">
                  <tr>
                    <th className="pb-4">Quarter</th>
                    <th className="pb-4">Decision</th>
                    <th className="pb-4">Net Result</th>
                    <th className="pb-4 text-right">Impact</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {history.slice().reverse().map((row, i) => (
                    <tr key={i} className="group transition-colors">
                      <td className="py-4 text-xs font-black text-slate-400 group-hover:text-blue-500 transition-colors">Q{row.quarter}</td>
                      <td className="py-4">
                        <div className="text-xs font-bold text-slate-900 capitalize">{row.action?.replace('_', ' ')}</div>
                        <div className="text-[10px] font-bold text-slate-400">{row.event || 'Organic Market'}</div>
                      </td>
                      <td className={`py-4 text-xs font-black ${row.profit >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                        ${row.profit.toLocaleString()}
                      </td>
                      <td className="py-4 text-right">
                        <span className={`text-[10px] font-black px-2 py-1 rounded-full ${row.reward >= 0.5 ? 'bg-blue-50 text-blue-600' : 'bg-slate-100 text-slate-500'}`}>
                          {formatNumber(row.reward)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="col-span-12 lg:col-span-6 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
             <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-2 text-slate-800">
                <div className="text-amber-500"><Trophy size={18} /></div>
                <h3 className="font-black text-xs uppercase tracking-widest">Global Leaderboard</h3>
              </div>
              <button className="text-[10px] font-black text-blue-600 hover:underline uppercase">View All</button>
            </div>
            <div className="space-y-4">
              {leaderboard.length > 0 ? leaderboard.map((entry, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-xl border border-slate-50 hover:border-blue-100 hover:bg-blue-50/30 transition-all group">
                  <div className="flex items-center gap-4">
                    <span className={`w-6 h-6 rounded-lg flex items-center justify-center text-[10px] font-black ${i < 3 ? 'bg-amber-100 text-amber-600' : 'bg-slate-100 text-slate-500'}`}>
                      {i + 1}
                    </span>
                    <div>
                      <div className="text-xs font-bold text-slate-900 group-hover:text-blue-700 transition-colors">{entry.name}</div>
                      <div className="text-[10px] font-bold text-slate-400">Quarter {entry.quarter} · ${entry.profit.toLocaleString()}</div>
                    </div>
                  </div>
                  <div className="text-xs font-black text-slate-900">
                    {formatNumber(entry.reward)}
                  </div>
                </div>
              )) : (
                <div className="flex flex-col items-center justify-center h-[300px] text-slate-400">
                   <Trophy size={48} className="opacity-10 mb-4" />
                   <p className="text-xs font-bold uppercase tracking-widest opacity-40">No records found</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      {/* Persistence / End State */}
      {state.done && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-slate-900/80 backdrop-blur-md p-4 animate-in fade-in duration-500">
          <div className="bg-white rounded-[32px] shadow-2xl max-w-lg w-full p-10 text-center animate-in zoom-in duration-300 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-blue-600 via-indigo-600 to-emerald-600"></div>
            <div className="mx-auto bg-blue-50 text-blue-600 w-20 h-20 rounded-3xl flex items-center justify-center mb-8 rotate-12">
              <Award size={40} />
            </div>
            <h2 className="text-3xl font-black text-slate-900 mb-4 tracking-tight">Operation Concluded</h2>
            <p className="text-slate-500 mb-10 text-lg font-medium leading-relaxed">
              {state.message}
            </p>
            <div className="grid grid-cols-2 gap-4 mb-10">
               <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100">
                 <div className="text-[10px] font-black text-slate-400 uppercase mb-1">Final Score</div>
                 <div className="text-2xl font-black text-blue-600">{formatNumber(state.reward)}</div>
               </div>
               <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100">
                 <div className="text-[10px] font-black text-slate-400 uppercase mb-1">Rank</div>
                 <div className="text-2xl font-black text-slate-900">#{state.market_rank}</div>
               </div>
            </div>
            <button 
              onClick={handleReset}
              className="w-full py-4 bg-slate-900 text-white rounded-2xl font-black text-sm uppercase tracking-widest hover:bg-slate-800 transition-all shadow-xl shadow-slate-200 active:scale-[0.98]"
            >
              Initialize New Session
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// --- Auth Components ---
const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);
      await login(formData);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid credentials');
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-6">
      <div className="max-w-md w-full">
        <div className="text-center mb-10">
          <div className="bg-blue-600 text-white w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-xl shadow-blue-900/20">
            <Shield size={32} />
          </div>
          <h1 className="text-3xl font-black text-white tracking-tight mb-2">Strategy Terminal</h1>
          <p className="text-slate-500 font-bold uppercase text-[10px] tracking-[0.2em]">Authorized Personnel Only</p>
        </div>
        
        <form onSubmit={handleSubmit} className="bg-slate-800 p-8 rounded-[32px] border border-slate-700 shadow-2xl">
          {error && <div className="bg-rose-500/10 border border-rose-500/20 text-rose-500 text-xs font-bold p-4 rounded-xl mb-6">{error}</div>}
          <div className="space-y-5">
            <div>
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 block">Enterprise ID</label>
              <input 
                type="email" 
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@corp.com"
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-600 outline-none focus:ring-2 focus:ring-blue-500 transition-all font-medium"
              />
            </div>
            <div>
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 block">Access Key</label>
              <input 
                type="password" 
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-600 outline-none focus:ring-2 focus:ring-blue-500 transition-all font-medium"
              />
            </div>
            <button className="w-full py-4 bg-blue-600 text-white rounded-xl font-black text-sm uppercase tracking-widest hover:bg-blue-500 transition-all shadow-xl shadow-blue-900/20 active:scale-[0.98] mt-4">
              Access Terminal
            </button>
          </div>
        </form>
        <p className="text-center mt-8 text-slate-500 text-sm font-bold">
          No account? <Link to="/register" className="text-blue-500 hover:text-blue-400">Request Access</Link>
        </p>
      </div>
    </div>
  );
};

const RegisterPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const { register } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await register({ email, password, full_name: fullName });
      navigate('/login');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-6">
      <div className="max-w-md w-full">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-black text-white tracking-tight mb-2">Request Access</h1>
          <p className="text-slate-500 font-bold uppercase text-[10px] tracking-[0.2em]">Create your strategist profile</p>
        </div>
        
        <form onSubmit={handleSubmit} className="bg-slate-800 p-8 rounded-[32px] border border-slate-700 shadow-2xl">
          {error && <div className="bg-rose-500/10 border border-rose-500/20 text-rose-500 text-xs font-bold p-4 rounded-xl mb-6">{error}</div>}
          <div className="space-y-5">
            <div>
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 block">Full Name</label>
              <input 
                type="text" 
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="John Doe"
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-600 outline-none focus:ring-2 focus:ring-blue-500 transition-all font-medium"
              />
            </div>
            <div>
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 block">Enterprise ID</label>
              <input 
                type="email" 
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@corp.com"
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-600 outline-none focus:ring-2 focus:ring-blue-500 transition-all font-medium"
              />
            </div>
            <div>
              <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 block">Access Key</label>
              <input 
                type="password" 
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-600 outline-none focus:ring-2 focus:ring-blue-500 transition-all font-medium"
              />
            </div>
            <button className="w-full py-4 bg-emerald-600 text-white rounded-xl font-black text-sm uppercase tracking-widest hover:bg-emerald-500 transition-all shadow-xl shadow-emerald-900/20 active:scale-[0.98] mt-4">
              Initialize Profile
            </button>
          </div>
        </form>
        <p className="text-center mt-8 text-slate-500 text-sm font-bold">
          Already have access? <Link to="/login" className="text-blue-500 hover:text-blue-400">Terminal Login</Link>
        </p>
      </div>
    </div>
  );
};

// --- Helper UI Components ---
const StatCard = ({ label, value, icon, color }: { label: string, value: string, icon: any, color: string }) => {
  const colorClasses: any = {
    blue: "text-blue-600 bg-blue-50",
    emerald: "text-emerald-600 bg-emerald-50",
    rose: "text-rose-600 bg-rose-50",
    indigo: "text-indigo-600 bg-indigo-50"
  };
  return (
    <div className="flex items-center gap-4 p-4 rounded-2xl border border-slate-50 hover:border-slate-100 hover:bg-slate-50/50 transition-all group">
      <div className={`p-3 rounded-xl transition-all group-hover:scale-110 ${colorClasses[color]}`}>{icon}</div>
      <div>
        <div className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-0.5">{label}</div>
        <div className="text-lg font-black text-slate-900 tracking-tight">{value}</div>
      </div>
    </div>
  );
};

const MiniStat = ({ label, value }: { label: string, value: any }) => (
  <div className="text-center">
    <div className="text-[8px] font-black text-slate-400 uppercase tracking-tighter mb-1">{label}</div>
    <div className="text-xs font-black text-slate-700">{value}</div>
  </div>
);

const ActionBtn = ({ label, onClick, icon }: { label: string, onClick: () => void, icon?: string }) => (
  <button 
    onClick={onClick}
    className="flex flex-col items-center justify-center gap-1.5 p-3 bg-slate-50 border border-slate-100 rounded-2xl hover:border-blue-200 hover:bg-blue-50 transition-all group active:scale-95"
  >
    <span className="text-xl group-hover:scale-125 transition-all grayscale-[0.5] group-hover:grayscale-0">{icon}</span>
    <span className="text-[10px] font-bold text-slate-500 group-hover:text-blue-600">{label}</span>
  </button>
);

const ChartCard = ({ title, icon, children, className }: { title: string, icon: any, children: any, className?: string }) => (
  <div className={`bg-white p-6 rounded-2xl shadow-sm border border-slate-200 relative ${className}`}>
    <div className="flex items-center gap-2 mb-8 text-slate-800">
      <div className="text-blue-500">{icon}</div>
      <h3 className="font-black text-xs uppercase tracking-widest">{title}</h3>
    </div>
    {children}
  </div>
);

// --- Main App Entry ---
const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
