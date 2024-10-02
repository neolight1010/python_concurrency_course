import logging
import os

from logger import logger
from yaml_reader import YamlPipelineExecutor


def main() -> None:
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    pipeline_location = os.environ.get("PIPELINE_LOCATION", "wiki_yahoo_scraper_pipeline.yaml")
    pipeline = YamlPipelineExecutor(pipeline_location)
    pipeline.start()

    pipeline.join()


if __name__ == "__main__":
    main()
