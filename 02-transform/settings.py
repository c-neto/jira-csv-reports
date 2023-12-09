from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=[
        "config/settings.yaml"
    ]
)
