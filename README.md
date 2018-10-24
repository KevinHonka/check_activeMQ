# check_activeMQ

This repository provides a check that is able to query the Jolokia API of activeMQ services and provide detailed metrics.

## Usage
usage: check_active_mq.py [-h] [--host HOST] [-u USERNAME] [-p PASSWORD] {queue,health}

positional arguments:
  {queue,health}

optional arguments:

  -h, --help            show this help message and exit
  
  --host HOST           Host of the Apache-MQ REST service
  
  -u USERNAME, --username USERNAME Username to be used to login
  
  -p PASSWORD, --password PASSWORD Password to be used to login

### Queue
usage: check_active_mq.py queue [-h] [-b BROKER] -q QUEUE [-c CRIT] [-w WARN]

optional arguments:

  -h, --help            show this help message and exit
  
  -b BROKER, --broker BROKER Brokername used to determine which broker to check. Defaults to localhost
  
  -q QUEUE, --queue QUEUE Queuename which is needed
  
  -c CRIT, --crit CRIT  Critical Value for the Queuesize
  
  -w WARN, --warn WARN  Warning Value for the Queuesize
