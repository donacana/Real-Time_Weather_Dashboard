function WeatherCard({ title, value, unit }) {
  return (
    <div className="weather-card">
      <p className="weather-card-title">{title}</p>

      <div className="weather-card-value">
        <span>{value ?? "-"}</span>
        <small>{unit}</small>
      </div>
    </div>
  );
}

export default WeatherCard;