
import threading
import time
from loguru import logger
from locusum_ingestor.worker import run_worker
from locusum_ingestor.ai_worker import run_ai_worker

def main():
    logger.info("Starting Locusum Ingestor Services (ETL + AI)...")

    # Create threads for each worker
    etl_thread = threading.Thread(target=run_worker, name="ETL-Worker", daemon=True)
    ai_thread = threading.Thread(target=run_ai_worker, name="AI-Worker", daemon=True)

    # Start threads
    etl_thread.start()
    ai_thread.start()

    # Keep main thread alive to monitor (or join)
    try:
        while True:
            time.sleep(1)
            if not etl_thread.is_alive():
                logger.error("ETL Worker died! Restarting/Exiting...")
                break
            if not ai_thread.is_alive():
                logger.error("AI Worker died! Restarting/Exiting...")
                break
    except KeyboardInterrupt:
        logger.info("Stopping services...")

if __name__ == "__main__":
    main()
