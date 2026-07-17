"use client";

import { useEffect, useState } from "react";
import axios from "axios";

export default function ClientsPage() {
  const [trust, setTrust] = useState<Record<string, number>>({});
  const [alerts, setAlerts] = useState<string[]>([]);

  const fetchData = async () => {
    try {
      const trustRes = await axios.get("http://localhost:8000/trust");
      const alertsRes = await axios.get("http://localhost:8000/alerts");

      setTrust(trustRes.data);
      setAlerts(alertsRes.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  // Detect status
  const getStatus = (id: string, score: number) => {
    if (alerts.some((a) => a.includes(id) && a.includes("Blocked")))
      return "Blocked";
    if (score < 0.3) return "Suspicious";
    return "Active";
  };

  return (
    <div className="p-6">

      <h1 className="text-2xl font-bold mb-6">👥 Clients Overview</h1>

      <div className="bg-gray-800 rounded-xl shadow-lg overflow-hidden">

        <table className="w-full text-left">
          <thead className="bg-gray-700 text-gray-300 text-sm">
            <tr>
              <th className="p-4">Client ID</th>
              <th className="p-4">Trust Score</th>
              <th className="p-4">Status</th>
            </tr>
          </thead>

          <tbody>
            {Object.entries(trust).map(([id, score]) => {
              const status = getStatus(id, score);

              return (
                <tr
                  key={id}
                  className="border-b border-gray-700 hover:bg-gray-700/40 transition"
                >
                  <td className="p-4 font-mono">
                    {id.substring(0, 10)}
                  </td>

                  <td className="p-4">
                    {score.toFixed(2)}
                  </td>

                  <td className="p-4">
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${
                        status === "Active"
                          ? "bg-green-500/20 text-green-400"
                          : status === "Suspicious"
                          ? "bg-yellow-500/20 text-yellow-400"
                          : "bg-red-500/20 text-red-400"
                      }`}
                    >
                      {status}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

      </div>
    </div>
  );
}