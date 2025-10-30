'use client';

import { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  MessageSquare, 
  Users, 
  DollarSign,
  Clock,
  ThumbsUp
} from 'lucide-react';

interface AnalyticsData {
  realtime: {
    active_conversations: number;
    total_conversations: number;
    total_messages: number;
    avg_sentiment: number;
  };
  trends: {
    daily_data: Array<{
      date: string;
      conversations: number;
      messages: number;
      sentiment: number;
      resolution_rate: number;
      cost: number;
    }>;
    summary: {
      total_conversations: number;
      total_messages: number;
      avg_sentiment: number;
      avg_resolution_rate: number;
      total_cost: number;
      cost_trend: string;
      volume_trend: string;
      sentiment_trend: string;
    };
  };
  costs: {
    models: Array<{
      model: string;
      requests: number;
      total_cost: number;
      avg_cost_per_request: number;
    }>;
    total_cost: number;
    total_requests: number;
  };
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export function AnalyticsDashboard({ agentId }: { agentId: string }) {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(30); // days

  useEffect(() => {
    fetchAnalytics();
    // Refresh every 30 seconds
    const interval = setInterval(fetchAnalytics, 30000);
    return () => clearInterval(interval);
  }, [agentId, timeRange]);

  const fetchAnalytics = async () => {
    try {
      const [realtimeRes, trendsRes, costsRes] = await Promise.all([
        fetch(`/api/v1/analytics/${agentId}/realtime`),
        fetch(`/api/v1/analytics/${agentId}/trends?days=${timeRange}`),
        fetch(`/api/v1/analytics/${agentId}/costs?days=${timeRange}`)
      ]);

      const analytics: AnalyticsData = {
        realtime: await realtimeRes.json(),
        trends: await trendsRes.json(),
        costs: await costsRes.json()
      };

      setData(analytics);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      setLoading(false);
    }
  };

  if (loading || !data) {
    return <div className="flex items-center justify-center h-96">Loading analytics...</div>;
  }

  const trendIcon = (trend: string) => {
    if (trend === 'increasing') return <TrendingUp className="text-green-500" />;
    if (trend === 'decreasing') return <TrendingDown className="text-red-500" />;
    return <span className="text-gray-500">—</span>;
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Customer Insights Analytics</h1>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(Number(e.target.value))}
          className="border rounded px-4 py-2"
        >
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      {/* Real-time KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Active Conversations"
          value={data.realtime.active_conversations}
          icon={<MessageSquare />}
          trend={data.trends.summary.volume_trend}
        />
        <KPICard
          title="Total Conversations"
          value={data.trends.summary.total_conversations}
          icon={<Users />}
          trend={data.trends.summary.volume_trend}
        />
        <KPICard
          title="Avg Sentiment"
          value={`${(data.trends.summary.avg_sentiment * 100).toFixed(1)}%`}
          icon={<ThumbsUp />}
          trend={data.trends.summary.sentiment_trend}
        />
        <KPICard
          title="Total Cost"
          value={`$${data.trends.summary.total_cost.toFixed(2)}`}
          icon={<DollarSign />}
          trend={data.trends.summary.cost_trend}
        />
      </div>

      {/* Conversation Volume Over Time */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Conversation Volume</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data.trends.daily_data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="conversations" 
              stroke="#8884d8" 
              name="Conversations"
            />
            <Line 
              type="monotone" 
              dataKey="messages" 
              stroke="#82ca9d" 
              name="Messages"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Sentiment & Resolution Trends */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Sentiment Trend</h2>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={data.trends.daily_data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[0, 1]} />
              <Tooltip />
              <Line 
                type="monotone" 
                dataKey="sentiment" 
                stroke="#FF8042" 
                name="Sentiment Score"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Resolution Rate</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={data.trends.daily_data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar 
                dataKey="resolution_rate" 
                fill="#00C49F" 
                name="Resolution %"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Model Cost Breakdown */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Cost by AI Model</h2>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data.costs.models}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={(entry) => entry.model}
                outerRadius={80}
                fill="#8884d8"
                dataKey="total_cost"
              >
                {data.costs.models.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>

          <div className="space-y-2">
            <h3 className="font-semibold">Model Usage Details</h3>
            {data.costs.models.map((model, idx) => (
              <div key={idx} className="flex justify-between items-center border-b py-2">
                <div>
                  <div className="font-medium">{model.model}</div>
                  <div className="text-sm text-gray-500">{model.requests} requests</div>
                </div>
                <div className="text-right">
                  <div className="font-semibold">${model.total_cost.toFixed(4)}</div>
                  <div className="text-sm text-gray-500">
                    ${model.avg_cost_per_request.toFixed(6)}/req
                  </div>
                </div>
              </div>
            ))}
            <div className="flex justify-between pt-4 font-bold text-lg">
              <span>Total</span>
              <span>${data.costs.total_cost.toFixed(2)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Key Insights */}
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-6 rounded-lg">
        <h2 className="text-2xl font-bold mb-4">📊 Key Insights</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <div className="text-sm opacity-90">Avg Resolution Rate</div>
            <div className="text-3xl font-bold">
              {data.trends.summary.avg_resolution_rate.toFixed(1)}%
            </div>
          </div>
          <div>
            <div className="text-sm opacity-90">Cost per Conversation</div>
            <div className="text-3xl font-bold">
              ${(data.trends.summary.total_cost / data.trends.summary.total_conversations).toFixed(4)}
            </div>
          </div>
          <div>
            <div className="text-sm opacity-90">Messages per Day</div>
            <div className="text-3xl font-bold">
              {Math.round(data.trends.summary.total_messages / timeRange)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function KPICard({ 
  title, 
  value, 
  icon, 
  trend 
}: { 
  title: string; 
  value: string | number; 
  icon: React.ReactNode; 
  trend?: string;
}) {
  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold">{value}</p>
        </div>
        <div className="text-blue-500">{icon}</div>
      </div>
      {trend && (
        <div className="mt-2 text-sm flex items-center gap-1">
          {trend === 'increasing' && <TrendingUp size={16} className="text-green-500" />}
          {trend === 'decreasing' && <TrendingDown size={16} className="text-red-500" />}
          <span className={
            trend === 'increasing' ? 'text-green-500' : 
            trend === 'decreasing' ? 'text-red-500' : 
            'text-gray-500'
          }>
            {trend}
          </span>
        </div>
      )}
    </div>
  );
}
