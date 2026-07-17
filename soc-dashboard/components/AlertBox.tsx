type AlertType = "danger" | "warning" | "success";

export default function AlertBox({
  type,
  text,
}: {
  type: AlertType;
  text: string;
}) {
  const styles: Record<AlertType, string> = {
    danger: "bg-red-100 text-red-600",
    warning: "bg-yellow-100 text-yellow-700",
    success: "bg-green-100 text-green-600",
  };

  return (
    <div className={`p-3 rounded-lg ${styles[type]}`}>
      {text}
    </div>
  );
}