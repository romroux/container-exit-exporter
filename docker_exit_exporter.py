#!/usr/bin/env python3
from prometheus_client import start_http_server, Gauge
import docker
import time
import os
import logging
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('docker-exit-exporter')

# Port for exposing metrics
EXPORTER_PORT = int(os.environ.get('EXPORTER_PORT', 9090))
# Collection interval in seconds
COLLECTION_INTERVAL = int(os.environ.get('COLLECTION_INTERVAL', 15))

# List of labels to extract from containers
LABEL_PREFIXES = [
    "com.docker.stack.namespace",
    "com.docker.swarm.node.id",
    "com.docker.swarm.service.id",
    "com.docker.swarm.service.name",
    "com.docker.swarm.task",
    "com.docker.swarm.task.id",
    "com.docker.swarm.task.name",
    "com.rundeck.commit",
    "com.rundeck.version",
    "maintainer",
    "module",
    "org.opencontainers.image.created",
    "org.opencontainers.image.description",
    "org.opencontainers.image.documentation",
    "org.opencontainers.image.licenses",
    "org.opencontainers.image.ref_name",
    "org.opencontainers.image.revision",
    "org.opencontainers.image.source",
    "org.opencontainers.image.title",
    "org.opencontainers.image.url",
    "org.opencontainers.image.vendor",
    "org.opencontainers.image.version",
    "sha",
    "target",
    "type",
    "build_actor",
    "built_at"
]

# Convert Docker labels to cAdvisor format
def docker_to_cadvisor_label(label):
    # Replace dots with underscores and add container_label_ prefix
    return f"container_label_{label.replace('.', '_')}"

# Metric for exit codes with specified labels
container_exit_code = Gauge(
    'container_exit_code',
    'Exit code of terminated containers',
    [
        'id',
        'image',
        'name',
        'container_label_build_actor',
        'container_label_built_at',
        'container_label_com_docker_stack_namespace',
        'container_label_com_docker_swarm_node_id',
        'container_label_com_docker_swarm_service_id',
        'container_label_com_docker_swarm_service_name',
        'container_label_com_docker_swarm_task',
        'container_label_com_docker_swarm_task_id',
        'container_label_com_docker_swarm_task_name',
        'container_label_com_rundeck_commit',
        'container_label_com_rundeck_version',
        'container_label_maintainer',
        'container_label_module',
        'container_label_org_opencontainers_image_created',
        'container_label_org_opencontainers_image_description',
        'container_label_org_opencontainers_image_documentation',
        'container_label_org_opencontainers_image_licenses',
        'container_label_org_opencontainers_image_ref_name',
        'container_label_org_opencontainers_image_revision',
        'container_label_org_opencontainers_image_source',
        'container_label_org_opencontainers_image_title',
        'container_label_org_opencontainers_image_url',
        'container_label_org_opencontainers_image_vendor',
        'container_label_org_opencontainers_image_version',
        'container_label_sha',
        'container_label_target',
        'container_label_type'
    ]
)

def collect_metrics():
    client = docker.from_env()

    # Reset metrics
    container_exit_code._metrics.clear()

    try:
        containers = client.containers.list(all=True)
        for container in containers:
            try:
                details = client.api.inspect_container(container.id)

                # Get basic information
                container_id = f"/docker/{container.id}"
                name = details.get('Name', '').lstrip('/')
                image = container.image.tags[0] if container.image.tags else container.image.id

                # If the image contains a SHA256, keep it intact
                if '@sha256:' in image:
                    image = image

                # Get Docker labels and convert to cAdvisor format
                container_labels = details.get('Config', {}).get('Labels', {})

                # Prepare labels for Prometheus
                label_values = {
                    'id': container_id,
                    'image': image,
                    'name': name,
                }

                # Add all required cAdvisor labels with empty default values
                for prefix in LABEL_PREFIXES:
                    cadvisor_label = docker_to_cadvisor_label(prefix)
                    docker_label = prefix

                    # If it's an OpenContainers label, check if it exists in container_labels
                    label_values[cadvisor_label] = container_labels.get(docker_label, '')

                # Container state and exit code
                state = details['State']['Status']
                if state not in ["running", "created", "restarting"]:
                    exit_code = details['State']['ExitCode']

                    # Record the metric
                    container_exit_code.labels(**label_values).set(exit_code)

                    if exit_code != 0:
                        logger.info(f"Container {name} exited with code {exit_code}")

            except Exception as e:
                logger.error(f"Error processing container {container.id[:12]}: {e}")

    except Exception as e:
        logger.error(f"Error collecting container metrics: {e}")

if __name__ == '__main__':
    # Start HTTP server
    start_http_server(EXPORTER_PORT)
    logger.info(f"Docker exit code exporter started on port {EXPORTER_PORT}")

    # Collection loop
    while True:
        collect_metrics()
        time.sleep(COLLECTION_INTERVAL)