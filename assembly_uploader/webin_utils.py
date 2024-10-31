import os

ENA_WEBIN = "ENA_WEBIN"
ENA_WEBIN_PASSWORD = "ENA_WEBIN_PASSWORD"


def ensure_webin_credentials_exist():
    if ENA_WEBIN not in os.environ:
        raise Exception(f"The variable {ENA_WEBIN} is missing from the env.")
    if ENA_WEBIN_PASSWORD not in os.environ:
        raise Exception(f"The variable {ENA_WEBIN_PASSWORD} is missing from the env")


def get_webin_credentials():
    ensure_webin_credentials_exist()
    webin = os.environ.get(ENA_WEBIN)
    password = os.environ.get(ENA_WEBIN_PASSWORD)
    return webin, password
