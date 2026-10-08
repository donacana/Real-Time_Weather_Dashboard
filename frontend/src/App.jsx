import { useEffect, useState } from "react";

import { fetchCurrentWeather } from "./api/weather";
import WeatherCard from "./components/WeatherCard";

import "./styles/dashboard.css";

function App() {
  const [weather, setWeather] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadWeather() {
    try {
      setError("");

      const data = await fetchCurrentWeather();

      setWeather(data);
    } catch (err) {
      console.error(err);
      setError("날씨 데이터를 불러오지 못했습니다.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadWeather();

    const intervalId = setInterval(() => {
      loadWeather();
    }, 10000);

    return () => {
      clearInterval(intervalId);
    };
  }, []);

  if (loading) {
    return (
      <div className="status-container">
        날씨 데이터를 불러오는 중...
      </div>
    );
  }

  if (error) {
    return (
      <div className="status-container error">
        {error}
      </div>
    );
  }

  const current = weather?.current;
  const units = weather?.current_units;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div>
          <p className="dashboard-label">
            REAL-TIME WEATHER DASHBOARD
          </p>

          <h1>서울 실시간 날씨</h1>

          <p className="location-info">
            위도 {weather?.latitude} / 경도 {weather?.longitude}
          </p>
        </div>

        <div className="updated-time">
          <span>최근 관측 시각</span>
          <strong>{current?.time ?? "-"}</strong>
        </div>
      </header>

      <section className="weather-grid">
        <WeatherCard
          title="현재 기온"
          value={current?.temperature_2m}
          unit={units?.temperature_2m ?? "°C"}
        />

        <WeatherCard
          title="체감 온도"
          value={current?.apparent_temperature}
          unit={units?.apparent_temperature ?? "°C"}
        />

        <WeatherCard
          title="습도"
          value={current?.relative_humidity_2m}
          unit={units?.relative_humidity_2m ?? "%"}
        />

        <WeatherCard
          title="강수량"
          value={current?.precipitation}
          unit={units?.precipitation ?? "mm"}
        />

        <WeatherCard
          title="강우량"
          value={current?.rain}
          unit={units?.rain ?? "mm"}
        />

        <WeatherCard
          title="구름량"
          value={current?.cloud_cover}
          unit={units?.cloud_cover ?? "%"}
        />

        <WeatherCard
          title="기압"
          value={current?.surface_pressure}
          unit={units?.surface_pressure ?? "hPa"}
        />

        <WeatherCard
          title="풍속"
          value={current.wind_speed_10m}
          unit={units.wind_speed_10m}
        />

        <WeatherCard
          title="풍향"
          value={current?.wind_direction_10m}
          unit={units?.wind_direction_10m ?? "°"}
        />

        <WeatherCard
          title="돌풍"
          value={current.wind_gusts_10m}
          unit={units.wind_gusts_10m}
        />
      </section>

      <section className="weather-detail">
        <div>
          <span>날씨 코드</span>
          <strong>{current?.weather_code ?? "-"}</strong>
        </div>

        <div>
          <span>해발고도</span>
          <strong>{weather?.elevation ?? "-"} m</strong>
        </div>

        <div>
          <span>시간대</span>
          <strong>{weather?.timezone ?? "-"}</strong>
        </div>

        <div>
          <span>갱신 주기</span>
          <strong>10초</strong>
        </div>
      </section>
    </div>
  );
}

export default App;