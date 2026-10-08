const API_BASE_URL = "http://localhost:8000";

export async function fetchCurrentWeather() {
  const response = await fetch(
    `${API_BASE_URL}/api/weather/current`
  );

  if (!response.ok) {
    throw new Error(
      `날씨 API 요청 실패: ${response.status}`
    );
  }

  return await response.json();
}