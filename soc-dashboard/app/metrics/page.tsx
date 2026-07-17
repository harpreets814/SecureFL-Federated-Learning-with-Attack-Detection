"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid
} from "recharts";

export default function MetricsPage() {
  const [metrics, setMetrics] = useState<any[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      const res = await axios.get("http://localhost:8000/metrics");
      setMetrics(res.data);
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">📊 Metrics</h1>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={metrics}>
          <CartesianGrid stroke="#444" />
          <XAxis dataKey="round" stroke="#ccc" />
          <YAxis stroke="#ccc" />
          <Tooltip />
          <Line dataKey="accuracy" stroke="#3b82f6" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}