export default function Card({ title, value, color }: any) {
  return (
    <div className="p-4 rounded-2xl shadow-md bg-[var(--card)] border border-[var(--border)]">
      <p className="text-sm text-[var(--muted)]">{title}</p>
      <h2 className={`text-2xl font-bold mt-2 ${color}`}>
        {value}
      </h2>
    </div>
  );
}