"""Helper class to access the QA Metrics API."""

import requests


class QAMetrics:
    """API access to the QA Metrics system."""

    def __init__(self, namespace, service="ska-sdp-qa-api"):
        """
        Initialises QA Metrics class
        :param namespace: k8s namespace
        :param service: name of the service
        :return: None
        """
        self._namespace = namespace
        self._url = f"http://{service}.{namespace}.svc:8002"

    def generate_display_url(self):
        """
        Create a URL that could be used to get to the display.
        :return: url
        """
        return f"/{self._namespace}/signal/display/"

    def spectogram(
        self, antenna1, antenna2, polarisation, img_type="thumbnail"
    ):
        """
        Get the bitmap image, of one of the waterfall plots.
        :param antenna1: the first antenna
        :param antenna2: the second antenna
        :param polarisation: the polarisation
        :param img_type: the image type, either 'full_image' or 'thumbnail'
        :return: image
        """
        if img_type not in ["full_image", "thumbnail"]:
            raise ValueError(
                "img_type is only allowed to be 'full_image' or 'thumbnail'"
            )
        image = requests.get(
            f"{self._url}/spectograms/{img_type}/"
            f"{antenna1}/{antenna2}/{polarisation}",
            timeout=5,
        )
        return image.content

    def speed2_latest_event(self, scan_id="latest"):
        """
        Get the latest event for the provided scan_id.
        :param scan_id: scan id
        :return: latest event
        """
        response = requests.get(
            f"{self._url}/stats/spead2/scans/{scan_id}/latest_event", timeout=5
        )
        return response.json()

    def speed2_all_events(self, scan_id="latest"):
        """
        Get the all events for the provided scan_id.
        :param scan_id: scan id
        :return: all events
        """
        response = requests.get(
            f"{self._url}/stats/spead2/scans/{scan_id}/all_events", timeout=5
        )
        return response.json()

    def scan_ids(self):
        """
        Get all known Scan IDs.
        :return: scan ids
        """
        response = requests.get(f"{self._url}/stats/spead2/scans", timeout=5)
        return response.json()

    def processing_blocks(self):
        """
        Get all known Processing Blocks.
        :return: processing blocks
        """
        response = requests.get(
            f"{self._url}/stats/processing_block/blocks", timeout=5
        )
        return response.json()

    def processing_block_latest_event(self, block_id="latest"):
        """
        Get the latest processing block event for the provided block_id.
        :param block_id: block id
        :return: latest event
        """
        response = requests.get(
            f"{self._url}/stats/processing_block/blocks/{block_id}/"
            "latest_event",
            timeout=5,
        )
        return response.json()

    def processing_block_all_events(self, block_id="latest"):
        """
        Get the all processing block events for the provided block_id.
        :param block_id: block id
        :return: all events
        """
        response = requests.get(
            f"{self._url}/stats/processing_block/blocks/{block_id}/all_events",
            timeout=5,
        )
        return response.json()

    def processing_block_baselines(self, block_id="latest"):
        """
        Get the baselines for the provided processing block.
        :param block_id: block id
        :return: baselines
        """
        response = requests.get(
            f"{self._url}/stats/processing_block/blocks/{block_id}/baselines",
            timeout=5,
        )
        baselines = response.json()["baselines"]
        baselines = []
        for baseline in response.json()["baselines"]:
            baseline_split = baseline.split("_")
            baselines.append(
                {
                    "antenna1": baseline_split[0],
                    "antenna2": baseline_split[1],
                    "polarisation": baseline_split[2],
                }
            )
        return baselines

    def processing_block_stats(self, block_id="latest"):
        """
        Get the stats for the provided processing block.
        :param block_id: block id
        :return: processing block state
        """
        response = requests.get(
            f"{self._url}/stats/processing_block/blocks/{block_id}/statistics",
            timeout=5,
        )
        return response.json()

    def generate_generator(self, kafka_host=None) -> dict:
        """
        Generate the config for the generator.
        :param kafka_host: kafka host
        :return: generator config
        """
        if kafka_host is None:
            kafka_host = f"ska-sdp-qa-kafka.{self._namespace}:9092"

        return {
            "name": "qa-metrics-generator-plasma-receiver",
            "image": "artefact.skao.int/ska-sdp-qa-metric-generator",
            "version": "0.14.2",
            "command": [
                "plasma-processor",
                "ska_sdp_qa_metric_generator.plasma_to_qa.SignalDisplay",
                "--plasma_socket",
                "/plasma/socket",
                "--readiness-file",
                "/tmp/processor_ready",
                "--use-sdp-metadata",
                "False",
            ],
            "readinessProbe": {
                "initialDelaySeconds": 5,
                "periodSeconds": 5,
                "exec": {"command": ["cat", "/tmp/processor_ready"]},
            },
            "env": [{"name": "BROKER_INSTANCE", "value": kafka_host}],
        }

    def generate_lmc_config(self, kafka_host=None) -> dict:
        """
        Generate the LMC config for the stats.
        :param kafka_host: kafka host
        :return: LMC config
        """
        if kafka_host is None:
            kafka_host = f"ska-sdp-qa-kafka.{self._namespace}:9092"

        return {
            "dtype": "json",
            "shape": [],
            "source": {
                "type": "KafkaConsumerSource",
                "servers": kafka_host,
                "topic": "metrics-receive_state-01",
                "encoding": "utf-8",
            },
            "sink": {
                "type": "TangoJsonScatterAttributeSink",
                "attributes": [
                    {
                        "attribute_name": "receiver_state",
                        "filter": "type=='visibility_receive'",
                        "path": "state",
                        "dtype": "str",
                        "default_value": "unknown",
                    },
                    {
                        "attribute_name": "last_update",
                        "filter": "type=='visibility_receive'",
                        "path": "time",
                        "dtype": "float",
                        "default_value": 0.0,
                    },
                    {
                        "attribute_name": "processing_block_id",
                        "filter": "type=='visibility_receive'",
                        "path": "processing_block_id",
                        "dtype": "str",
                        "default_value": "",
                    },
                    {
                        "attribute_name": "execution_block_id",
                        "filter": "type=='visibility_receive'",
                        "path": "execution_block_id",
                        "dtype": "str",
                        "default_value": "",
                    },
                    {
                        "attribute_name": "subarray_id",
                        "filter": "type=='visibility_receive'",
                        "path": "subarray_id",
                        "dtype": "str",
                        "default_value": "-1",
                    },
                    {
                        "attribute_name": "scan_id",
                        "filter": "type=='visibility_receive'",
                        "path": "scan_id",
                        "dtype": "int",
                        "default_value": 0,
                    },
                    {
                        "attribute_name": "payloads_received",
                        "filter": "type=='visibility_receive'",
                        "path": "payloads_received",
                        "dtype": "int",
                        "default_value": 0,
                    },
                    {
                        "attribute_name": "time_since_last_payload",
                        "filter": "type=='visibility_receive'",
                        "path": "time_since_last_payload",
                        "dtype": "float",
                        "default_value": 0.0,
                    },
                ],
            },
        }
