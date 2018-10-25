# check_activeMQ

This repository provides a check that is able to query the Jolokia API of activeMQ services and provide detailed metrics.

## Usage

`HOST` must be an FQDN followed by `PORT` and the full jolokia path: `http://localhost:8161/api/jolokia/`

```
usage: check_active_mq.py [-h] [--host HOST] [--port PORT] [-u USERNAME]
                          [-p PASSWORD]
                          {queue,health} ...

positional arguments:
  {queue,health}

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           Host of the Apache-MQ REST service
  --port PORT           Port of the Apache-MQ REST service
  -u USERNAME, --username USERNAME
                        Username to be used to login
  -p PASSWORD, --password PASSWORD
                        Password to be used to login
```

### Example

```
./check_active_mq.py --host "http://localhost:8161/api/jolokia/" health
Apache-MQ - OK
 Uptime: 42 minutes
 BrokerVersion: 5.15.6
 Store Usage in %: 0
 Memory Usage in %: 0
 Total Connections: 0
 Total Dequeue Count: 0
 Total Enqueue Count: 1
 | Store Usage=0;;;;100 Memory Usage=0;;;;100 Uptime=42 minutes;;;; Total Dequeue Count=0;;;; Total Enqueue Count=1;;;;

```


### Queue

```
usage: check_active_mq.py queue [-h] [-b BROKER] -q QUEUE [-c CRIT] [-w WARN]

optional arguments:

  -h, --help            show this help message and exit

  -b BROKER, --broker BROKER Brokername used to determine which broker to check. Defaults to localhost

  -q QUEUE, --queue QUEUE Queuename which is needed

  -c CRIT, --crit CRIT  Critical Value for the Queuesize

  -w WARN, --warn WARN  Warning Value for the Queuesize
```

### Health
```
usage: check_active_mq.py health [-h] [-b BROKER]

optional arguments:

  -h, --help            show this help message and exit

  -b BROKER, --broker BROKER Brokername used to determine which broker to check. Defaults to localhost
```
