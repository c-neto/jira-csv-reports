from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=[
        "config/.secrets.yaml",
        "config/settings.yaml"
    ]
)
