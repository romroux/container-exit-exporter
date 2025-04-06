# Docker Exit Code Exporter

A Prometheus exporter that captures and exposes exit codes from stopped Docker containers. This exporter is designed to work seamlessly with Docker Swarm and provides metrics with the same label format as cAdvisor for easy integration with existing monitoring setups.

## Features

- Captures exit codes from terminated Docker containers
- Compatible with Docker Swarm
- Uses the same label format as cAdvisor
- Lightweight Alpine-based image
- Secure non-root execution
- Automatic Docker socket permission handling

## Installation

### Using Docker

```bash
docker run -d --name docker-exit-exporter \
  -p 9090:9090 \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  ghcr.io/username/docker-exit-exporter:latest
```

### Using Docker Compose

```yaml
version: '3.8'

services:
  docker-exit-exporter:
    image: ghcr.io/username/docker-exit-exporter:latest
    ports:
      - "9090:9090"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
```

### Using Docker Swarm

```bash
docker stack deploy -c docker-stack.yml exit-exporter
```

## Configuration

The exporter can be configured using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `EXPORTER_PORT` | Port to expose metrics on | `9090` |
| `COLLECTION_INTERVAL` | Time between metric collections in seconds | `15` |

## Prometheus Configuration

Add the following to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'docker-exit-exporter'
    static_configs:
      - targets: ['docker-exit-exporter:9090']
```

## Metrics

The exporter provides the following metrics:

- `container_exit_code`: The exit code of stopped containers with labels matching cAdvisor format.

Example PromQL queries:

```
# Find all containers that exited with non-zero codes
container_exit_code > 0

# Count containers by exit code
count by(container_label_com_docker_swarm_service_name) (container_exit_code > 0)
```

## Building from Source

```bash
# Clone the repository
git clone https://github.com/username/docker-exit-exporter.git
cd docker-exit-exporter

# Build the Docker image
docker build -t docker-exit-exporter .

# Run the container
docker run -d -p 9090:9090 -v /var/run/docker.sock:/var/run/docker.sock:ro docker-exit-exporter
```

## How It Works

The exporter connects to the Docker daemon API using the mounted socket and periodically collects information about all containers. For containers that are not in the "running" state, it extracts their exit codes and exposes them as Prometheus metrics with all the container labels in the cAdvisor format.

## Security Considerations

- The exporter runs as a non-root user inside the container
- It automatically handles Docker socket permissions
- Only read-only access to the Docker socket is required

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by cAdvisor's container metrics format
- Built with Python and the Docker SDK

## Credits

This project was developed with significant assistance from:
- Claude AI (Anthropic) - Helped with code structure, documentation writing, and troubleshooting Docker permission issues

---

Made with ❤️ by Romain ROUX