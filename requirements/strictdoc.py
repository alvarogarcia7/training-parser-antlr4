from strictdoc.core.project_config import ProjectConfig

# From https://github.com/strictdoc-project/strictdoc/blob/main/strictdoc_config.py
def create_config() -> ProjectConfig:
    config = ProjectConfig(
        dir_for_sdoc_cache="requirements/output/_cache",
    )
    return config
