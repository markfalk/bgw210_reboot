# Arris BGW210 Reboot
This program will reboot the Arris BGW210

It will report to Slack via webhook that HTTP status code of the reboot command (302 is the correct response)

I find that the latency will start to increase sporadicaly if I don't reboot this thing every week.

It is published to dockerhub and I run it on a weekly schedule on
my Unraid server.

Script to invoke it looks like:

```bash
#!/bin/bash
docker run --rm -e PASSWORD=='<MODEM_PASSWORD>' -e SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXXX/XXXXX mfalk/bgw210_reboot
```

Supported environment variables:
| Variable | Purpose |
| --- | --- |
| PASSWORD | Password for the modem admin |
| SLACK_WEBHOOK_URL | Webhook URL to post to Slack the status of the reboot |
| DEBUG | Set to any value to print out response bodies |