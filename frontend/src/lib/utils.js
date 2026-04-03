function formatApiError(detail) {
  if (!detail) return "Prediction failed";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail))
    return detail
      .map((item) => (typeof item === "string" ? item : item?.msg || JSON.stringify(item)))
      .join(" | ");
  if (typeof detail === "object") return detail.msg || JSON.stringify(detail);
  return String(detail);
}

export { formatApiError };
