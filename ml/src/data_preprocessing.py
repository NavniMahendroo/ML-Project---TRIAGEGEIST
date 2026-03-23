import pandas as pd
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(config.LOGS_DIR, 'preprocessing.log')),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


def run():
    log.info('Loading raw datasets...')
    train = pd.read_csv(config.TRAIN_CSV)
    test = pd.read_csv(config.TEST_CSV)
    patient_history = pd.read_csv(config.PATIENT_HISTORY_CSV)
    chief_complaints = pd.read_csv(config.CHIEF_COMPLAINTS_CSV)

    log.info(f'Train shape: {train.shape} | Test shape: {test.shape}')

    # Drop target leakage columns from train
    log.info(f'Dropping leakage columns: {config.LEAKAGE_COLS}')
    train = train.drop(columns=config.LEAKAGE_COLS)

    # Merge patient history
    log.info('Merging patient_history...')
    train = train.merge(patient_history, on='patient_id', how='left')
    test = test.merge(patient_history, on='patient_id', how='left')

    # Merge chief complaints (raw text only)
    log.info('Merging chief_complaints (raw text)...')
    complaints_subset = chief_complaints[['patient_id', 'chief_complaint_raw']]
    train = train.merge(complaints_subset, on='patient_id', how='left')
    test = test.merge(complaints_subset, on='patient_id', how='left')

    log.info(f'Merged train shape: {train.shape} | Merged test shape: {test.shape}')

    os.makedirs(config.PROCESSED_DIR, exist_ok=True)
    train.to_parquet(config.TRAIN_PROCESSED, index=False)
    test.to_parquet(config.TEST_PROCESSED, index=False)
    log.info(f'Saved processed data to {config.PROCESSED_DIR}')


if __name__ == '__main__':
    run()
