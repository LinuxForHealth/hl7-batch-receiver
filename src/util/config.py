import os

from whi_caf_lib_configreader import config as configreader

# NOTE: Postgres configurations are handled by the whpa-cdp-lib-postgres lib.
#       See the whpa-cdp-lib-postgres code for detials (ENV vars, config keys, etc..) on configuration.
KAFKA_CONFIG_ENV = "WHPA_CDP_BATCH_RECEIVER_KAFKA_CONFIG"
MINIO_CONFIG_ENV = "WHPA_CDP_BATCH_RECEIVER_MINIO_CONFIG"
MINIO_SECRETS_ENV = "WHPA_CDP_MINIO_SECRETS"

minio_header = "minio"
minio_required_keys = ["MINIO_ENDPOINT", "MINIO_ROOT_USER", "MINIO_ROOT_PASSWORD"]

kafka_header = "kafka"
kafka_required_keys = ["BOOTSTRAP_SERVERS", "TOPIC"]


_configs = None


def _load_configs():
    global _configs

    kafka_config_file_path = os.getenv(KAFKA_CONFIG_ENV, "config/kafka.ini")
    minio_config_file_path = os.getenv(MINIO_CONFIG_ENV, "config/minio.ini")
    minio_secrets_folder = os.getenv(MINIO_SECRETS_ENV, "secrets/minio/")

    kafka_config = configreader.load_config(kafka_config_file_path)
    minio_config = configreader.load_config(
        minio_config_file_path, secrets_dir=[minio_secrets_folder]
    )

    configreader.validate_config(minio_config, minio_header, minio_required_keys)
    configreader.validate_config(kafka_config, kafka_header, kafka_required_keys)

    combined_configs = {**kafka_config, **minio_config}

    _configs = combined_configs


def get_config():
    if _configs is None:
        _load_configs()
    return _configs
