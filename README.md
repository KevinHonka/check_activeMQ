# check_activeMQ

This repository provides a check that is able to query the Jolokia API of activeMQ services and provide detailed metrics.

## Usage


```
usage: check_active_mq.py [-h] [--host HOST] [--port PORT] [-u USERNAME] [-p PASSWORD] --check CHECK [--broker BROKER] [-q QUEUE] [-c CRIT] [-w WARN]

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           Host of the Apache-MQ REST service
  --port PORT           Port of the Apache-MQ REST service (default: 8161)
  -u USERNAME, --username USERNAME
                        Username to be used to login
  -p PASSWORD, --password PASSWORD
                        Password to be used to login
  --check CHECK         'health' or 'queue'. With 'queue' the '--queue' parameter is required
  --broker BROKER       Brokername used to determine which broker to check. Defaults to localhost
  -q QUEUE, --queue QUEUE
                        Queuename which is required
  -c CRIT, --crit CRIT  Critical Value for the Queuesize
  -w WARN, --warn WARN  Warning Value for the Queuesize
```

### Example

```
check_active_mq.py --host $HOST -u $user -p $pass --check health


check_active_mq.py --host $HOST -u $user -p $pass --check queue --queue "ActiveMQ.DLQ" --warn 10 --crit 15
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
