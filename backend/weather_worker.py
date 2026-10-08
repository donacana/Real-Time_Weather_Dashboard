"""현재 날씨를 수집하고 작업 완료 후 60초마다 반복하는 독립 Worker."""

import logging
import time

if __package__:
    from .collect_weather import collect_weather
else:
    from collect_weather import collect_weather


def main():
    """즉시 수집을 시작하고 오류 후에도 다음 주기에 재시도한다."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("날씨 Worker 시작: Seoul, 수집 완료 후 60초 간격")
    try:
        while True:
            logger.info("날씨 수집 시작: Seoul")
            try:
                saved = collect_weather(37.5665, 126.9780, "Seoul")
                if saved:
                    logger.info("날씨 저장 성공: Seoul")
                else:
                    logger.info("중복 데이터: 동일 관측 시각 데이터가 이미 저장되어 있습니다.")
            except (RuntimeError, ValueError) as exc:
                logger.error("날씨 수집 실패: %s", exc)
            except Exception as exc:
                logger.error("날씨 수집 실패: 예기치 않은 오류 (%s)", type(exc).__name__)
            logger.info("60초 후 다음 수집을 시작합니다.")
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("날씨 Worker를 정상 종료합니다.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
