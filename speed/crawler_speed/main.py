from logging_config import setup_logging
from speed_ingest import SpeedIngestService
from config import Config
def main():
    setup_logging()
    service = SpeedIngestService(date=Config.REPLAY_DATE)
    service.run()

if __name__ == "__main__":
    main()
