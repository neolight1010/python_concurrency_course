from __future__ import annotations

import importlib
from multiprocessing import Queue
import threading
import time
from typing import Any, Protocol
import yaml

from logger import logger
from workers.done import DONE

class WorkerFactory(Protocol):
    def __call__(self, input_queue: Queue[Any] | None, output_queues: list[Queue[Any]] | None, *, input_values: list[str]) -> Worker:
        ...

class Worker(Protocol):
    def join(self) -> None:
        ...

    def is_alive(self) -> bool:
        ...

class YamlPipelineExecutor(threading.Thread):
    def __init__(self, pipeline_location: str) -> None:
        super().__init__()
        
        self._pipeline_location = pipeline_location
        self._queues: dict[str, Queue[Any]] = {}
        self._workers: dict[str, list[Worker]] = {}

        self._queue_consumers: dict[str, int] = {}
        self._downstream_queues: dict[str, list[str]] = {}

    def run(self) -> None:
        self._process_pipeline()

        while True:
            total_workers_alive = 0
            worker_stats: list[tuple[str, int]] = []
            
            workers_to_delete: list[str] = []
            for worker_name in self._workers:
                total_worker_threads_alive = len([True for worker_thread in self._workers[worker_name] if worker_thread.is_alive()])

                worker_stats.append((worker_name, total_worker_threads_alive))

                total_workers_alive += total_worker_threads_alive

                if total_worker_threads_alive == 0:
                    for downstream_queue in self._downstream_queues[worker_name]:
                        number_of_consumers = self._queue_consumers[downstream_queue]

                        for _ in range(number_of_consumers):
                            self._queues[downstream_queue].put(DONE)

                    workers_to_delete.append(worker_name)

            for worker_name in workers_to_delete:
                del self._workers[worker_name]

            if total_workers_alive == 0:
                break

            logger.debug(f"pipeline stats: {worker_stats}")
            time.sleep(1)

    def _process_pipeline(self) -> None:
        self._load_pipeline()
        self._initialize_queues()
        self._initialize_workers()

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

            worker_name: str = worker.get("name")
            input_queue_name: str | None = worker.get("input_queue")
            output_queue_names: list[str] | None = worker.get("output_queues")
            input_values: list[str] = worker.get("input_values") or []
            num_instances: int = worker.get("instances", 1)

            if input_queue_name is not None:
                self._queue_consumers[input_queue_name] = num_instances

            self._downstream_queues[worker_name] = output_queue_names or []

            input_queue = self._queues[input_queue_name] if input_queue_name is not None else None
            output_queues = [self._queues[output_queue] for output_queue in output_queue_names] if output_queue_names is not None else None

            worker_instances = [worker_factory(input_queue, output_queues, input_values=input_values) for _ in range(num_instances)]
            self._workers[worker_name] = worker_instances
