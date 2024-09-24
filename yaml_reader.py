from __future__ import annotations

import importlib
import itertools
from multiprocessing import Queue
from typing import Any, Protocol
import yaml

class WorkerFactory(Protocol):
    def __call__(self, input_queue: Queue[Any] | None, output_queues: list[Queue[Any]] | None) -> Worker:
        ...

class Worker(Protocol):
    def join(self) -> None:
        ...

class YamlPipelineExecutor:
    def __init__(self, pipeline_location: str) -> None:
        self._pipeline_location = pipeline_location
        self._queues: dict[str, Queue[Any]] = {}
        self._workers: dict[str, list[Worker]] = {}

    def process_pipeline(self) -> None:
        self._load_pipeline()
        self._initialize_queues()
        self._initialize_workers()

    # TODO We shouldn't use this method. Delete later
    def add_queue(self, name: str, queue: Queue[Any]) -> None:
        self._queues[name] = queue

    def join(self) -> None:
        for worker in itertools.chain(*self._workers.values()):
            worker.join()

    def _load_pipeline(self) -> None:
        with open(self._pipeline_location) as in_file:
            self._yaml_data = yaml.safe_load(in_file)

    def _initialize_queues(self) -> None:
        for queue in self._yaml_data["queues"]:
            queue_name: str = queue["name"]
            self._queues[queue_name] = Queue()

    def _initialize_workers(self) -> None:
        for worker in self._yaml_data["workers"]:
            worker_factory: WorkerFactory = getattr(importlib.import_module(worker["location"]), worker["class"])
            input_queue_name = worker.get("input_queue")
            output_queue_names = worker.get("output_queues")

            input_queue = self._queues[input_queue_name] if input_queue_name is not None else None
            output_queues = [self._queues[output_queue] for output_queue in output_queue_names] if output_queue_names is not None else None

            num_instances: int = worker.get("instances", 1)

            worker_instances = [worker_factory(input_queue, output_queues) for _ in range(num_instances)]
            self._workers[worker["name"]] = worker_instances
