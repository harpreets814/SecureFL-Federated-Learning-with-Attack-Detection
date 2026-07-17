"use client";

import { useEffect, useState } from "react";
import axios from "axios";

export default function SecurityPage() {
  const [alerts, setAlerts] = useState<string[]>([]);

  const fetchData = async () => {
    try {
      const res = await axios.get("http://localhost:8000/alerts");
      setAlerts(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-6 text-white bg-gray-900 min-h-screen">
      <h1 className="text-2xl font-bold mb-6">🔐 Security Monitoring</h1>

      <div className="bg-gray-800 p-5 rounded-xl shadow">
        <h2 className="text-lg font-semibold mb-4">🚨 Alerts</h2>

        {alerts.length === 0 ? (
          <p className="text-gray-400">No threats detected</p>
        ) : (
          alerts.map((a, i) => (
            <p
              key={i}
              className={`mb-2 ${
                a.includes("Blocked")
                  ? "text-red-400 font-bold"
                  : "text-yellow-400"
              }`}
            >
              {a}
            </p>
          ))
        )}
      </div>
    </div>
  );
}