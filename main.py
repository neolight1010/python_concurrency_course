import logging

from logger import logger
from yaml_reader import YamlPipelineExecutor


def main() -> None:
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    pipeline = YamlPipelineExecutor("wiki_yahoo_scraper_pipeline.yaml")
    pipeline.process_pipeline()


if __name__ == "__main__":
    main()
