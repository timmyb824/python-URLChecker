# python-URLChecker

This is a simple python tool that checks the status of a list of URLs and send a notification if any of the URLs are down based on the status code.

## Usage

First, create a `checks.yaml` file somewhere on your server. This file will contain the URLs you want to check and the status code you want to check for. Here is an example of the `checks.yaml` file:

```yaml
---
- name: github # Name of the check (only used for logging purposes)
  url: https://github.com # URL to check
  retries: 1 # Number of retries before sending a notification (0 to 5)
  status_accepted: # List of status codes that are considered acceptable
    - 200
    - 301

- name: code-server
  url: https://code-server.example.com
  retries: 2
  status_accepted:
    - 200
```

Next, create a `docker-compose.yaml` file with the following content:

```yaml
---
services:
  urlchecker:
    image: docker.io/timmyb824/python-urlchecker:latest
    container_name: urlchecker
    network_mode: host
    volumes:
      - "./checks.yaml:/app/checks.yaml" # update with path to your checks.yaml file
    environment:
      # - APPRISE_DISCORD=${APPRISE_DISCORD}
      # - APPRISE_GOTIFY=${APPRISE_GOTIFY}
      # - TIME_BETWEEN_SCHEDULED_CHECKS=${TIME_BETWEEN_SCHEDULED_CHECKS} # Optional: default is 60 seconds
    restart: unless-stopped
```

You'll notice that there are some environment variables that are commented out. Youll want to setup at least one notification service. The tool usees [Apprise](https://github.com/caronc/apprise) to send notifications. You can use any of the [supported notification services](https://github.com/caronc/apprise#supported-notifications). The only requirement is that the environment variable must be in the format `APPRISE_<SERVICE_NAME>`. For example, to setup a Discord notification, you would set the `APPRISE_DISCORD` environment variable to your Discord webhook URL. You can have multiple notification services setup by adding more environment variables.

Finally, run the following command to start the container:

```bash
docker-compose up -d
```

Example output:

```bash
2024-04-07 21:23:44,990 - INFO - Result for: watchyourlan - https://wyl.example.com -- 200
2024-04-07 21:23:44,990 - INFO - Saving status to file: status.yaml
2024-04-07 21:23:45,066 - INFO - Result for: zipline - https://zipline.example.com -- 200
2024-04-07 21:23:45,066 - INFO - Saving status to file: status.yaml
```

To keep track of the status of the URLs, the tool saves the status of the URLs to a `status.yaml` file. This file is used to determine if a notification should be sent based on the number of retries specified in the `checks.yaml` file.

## Final Notes

There are many tools out there that do the same thing. This tool was created to be simple and easy to use. I have a homelab where I run a bunch of services and I just wanted a simple tool to check the status of internal URLs and send me a notification if any of the URLs are down. This tool is not meant to be a replacement for more robust monitoring tools like [Uptime-Kuma](https://github.com/louislam/uptime-kuma) or [Monika](https://monika.hyperjump.tech/) to name a few.

Please note, this tool may have bugs or imperfections. If you find any issues or have suggestions, please feel free to open an issue or submit a pull request.
