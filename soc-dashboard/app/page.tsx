"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
} from "recharts";

export default function Dashboard() {
  const [alerts, setAlerts] = useState<string[]>([]);
  const [trust, setTrust] = useState<Record<string, number>>({});
  const [metrics, setMetrics] = useState<any[]>([]); // ✅ NEW
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const alertsRes = await axios.get("http://localhost:8000/alerts");
      const trustRes = await axios.get("http://localhost:8000/trust");
      const metricsRes = await axios.get("http://127.0.0.1:8000/metrics"); // ✅ NEW


      // ✅ STEP 1: remove duplicates (keep latest per round)
      const uniqueMap: any = {};

      metricsRes.data.forEach((m: any) => {
        uniqueMap[m.round] = m;
      });

      // ✅ STEP 2: convert to array
      const cleanMetrics = Object.values(uniqueMap);

      // ✅ STEP 3: sort by round
      cleanMetrics.sort((a: any, b: any) => a.round - b.round);

      // ✅ STEP 4: replace state (IMPORTANT — no append)
      // take LAST 15 AFTER sorting
      const latest = cleanMetrics.slice(
        Math.max(cleanMetrics.length - 15, 0)
      );

      setMetrics(latest);


      setAlerts(alertsRes.data);
      setTrust(trustRes.data);


      setLoading(false);
    } catch (err) {
      console.error("API error:", err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  const trustData = Object.entries(trust).map(([id, score]) => ({
    name: id.substring(0, 6),
    trust: score,
  }));

  const smoothedMetrics = metrics.map((m, i, arr) => {
    if (i === 0) return m;

    const prev = arr[i - 1];
    return {
      ...m,
      accuracy: (prev.accuracy + m.accuracy) / 2,
    };
  });

  const suspiciousCount = Object.values(trust).filter((t) => t < 0.3).length;

  return (
    <div className="space-y-6">

      {/* 🔥 STATUS BAR */}
      <div className="card flex justify-between items-center">
        <div>
          <h2 className="text-lg font-semibold">System Status</h2>
          <p className="text-sm text-[var(--muted)]">
            Federated Learning Network Active
          </p>
        </div>

        <div className="flex items-center gap-2 text-green-400 font-semibold">
          <span className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
          LIVE
        </div>
      </div>

      {/* 🔥 KPI CARDS (UPGRADED) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">

        <div className="card hover:scale-[1.02] transition">
          <p className="text-sm text-[var(--muted)]">Total Clients</p>
          {loading ? (
            <div className="h-6 w-16 skeleton mt-2"></div>
          ) : (
            <h2 className="text-3xl font-bold text-blue-400">
              {Object.keys(trust).length}
            </h2>
          )}
        </div>

        <div className="card hover:scale-[1.02] transition">
          <p className="text-sm text-[var(--muted)]">Threats Detected</p>
          {loading ? (
            <div className="h-6 w-16 skeleton mt-2"></div>
          ) : (
            <h2 className="text-3xl font-bold text-yellow-400">
              {alerts.length}
            </h2>
          )}
        </div>

        <div className="card hover:scale-[1.02] transition">
          <p className="text-sm text-[var(--muted)]">Suspicious Clients</p>
          {loading ? (
            <div className="h-6 w-16 skeleton mt-2"></div>
          ) : (
            <h2 className="text-3xl font-bold text-red-400">
              {suspiciousCount}
            </h2>
          )}
        </div>

      </div>

      {/* 🚨 ALERTS (UPGRADED) */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-3">🚨 Security Alerts</h2>

        {loading ? (
          <div className="space-y-2">
            <div className="h-4 skeleton"></div>
            <div className="h-4 skeleton"></div>
          </div>
        ) : alerts.length === 0 ? (
          <p className="text-[var(--muted)]">No alerts</p>
        ) : (
          alerts.map((a, i) => (
            <div
              key={i}
              className={`p-3 rounded-lg mb-2 flex items-center gap-2 border ${
                a.includes("Blocked")
                  ? "bg-red-500/10 border-red-500 text-red-400 animate-pulse"
                  : "bg-yellow-500/10 border-yellow-500 text-yellow-400"
              }`}
            >
              ⚠️ {a}
            </div>
          ))
        )}
      </div>

      {/* 🔥 TRUST + BAR CHART */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

        {/* TRUST */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-3">Trust Scores</h2>

          {loading ? (
            <div className="space-y-3">
              <div className="h-3 skeleton"></div>
              <div className="h-3 skeleton"></div>
            </div>
          ) : (
            Object.entries(trust).map(([id, score]) => (
              <div key={id} className="mb-3">
                <p className="text-sm">
                  {id.substring(0, 6)} → {score.toFixed(2)}
                </p>

                <div className="w-full bg-gray-700 rounded-full h-2 mt-1">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      score < 0.3 ? "bg-red-500" : "bg-green-500"
                    }`}
                    style={{ width: `${score * 100}%` }}
                  />
                </div>
              </div>
            ))
          )}
        </div>

        {/* BAR CHART */}
        <div className="card">
          <h2 className="text-xl font-semibold mb-3">Trust Distribution</h2>

          {loading ? (
            <div className="h-[250px] skeleton"></div>
          ) : (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={trustData}>
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip />
                <Bar dataKey="trust" fill="#22c55e" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

      </div>

      {/* 🔥 ACCURACY GRAPH */}
      {/* 🔥 REAL-TIME GRAPH */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-3">Accuracy vs Rounds</h2>

        {/* ✅ TREND INDICATOR */}
        <p className="text-sm text-[var(--muted)] mb-2">
          Trend: {
            metrics.length > 1 &&
            metrics.at(-1)?.accuracy > metrics.at(-2)?.accuracy
              ? "📈 Improving"
              : "📉 Dropping"
          }
        </p>

        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={smoothedMetrics}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis
              dataKey="round"
              stroke="#94a3b8"
              tick={{ fontSize: 12 }}
              interval="preserveStartEnd"
            />

            <YAxis domain={[0, 1]} stroke="#94a3b8" />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="accuracy"
              stroke="#3b82f6"
              strokeWidth={3}

              dot={{ r: 4 }}
              activeDot={{ r: 5 }}
              
              isAnimationActive={true}
              animationDuration={500}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 🔥 ASR GRAPH (SECURITY PERFORMANCE) */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-3">Attack Success Rate (ASR)</h2>

        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={metrics}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />

            <XAxis dataKey="round" stroke="#94a3b8" />
            <YAxis domain={[0, 1]} stroke="#94a3b8" />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="asr"
              stroke="#ef4444"
              strokeWidth={3}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      

    </div>
  );
}