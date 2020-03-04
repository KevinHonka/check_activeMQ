#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import json
import logging
import sys
from enum import Enum
from types import SimpleNamespace

import requests
from requests import RequestException, ConnectionError, URLRequired, TooManyRedirects, Timeout


class CheckApacheMQ(object):
    """docstring for Check_Apache_MQ."""

    class ExitCode(Enum):
        """
        Enum Class to better select ExitCodes
        """
        OK = 0
        WARNING = 1
        CRITICAL = 2
        UNKNOWN = 3

    def __init__(self, host, port, user, password):

        self.host = host
        self.port = port
        self.user = user
        self.password = password

        self.log = logging.getLogger('CheckApacheMQ')
        streamhandler = logging.StreamHandler(sys.stdout)
        self.log.addHandler(streamhandler)
        self.log.setLevel(logging.INFO)

    def url(self, broker, destination=None):
        """
          generates a uniq url
        """
        url = "http://{host:}:{port:}/api/jolokia/read/org.apache.activemq:type=Broker,brokerName={broker:}"

        if destination:
            url += ",destinationType=Queue,destinationName={destination:}"

        url = url.format(host=self.host, port=self.port, broker=broker, destination=destination)

        return url

    def get_health_status(self, broker_name):
        """
        """
        data = self.query_amq(self.url(broker_name), auth=(self.user, self.password))

        if not data:
            sys.exit(self.ExitCode.UNKNOWN.value)

        values = data.get('value', {})

        if not values:
            sys.exit(self.ExitCode.UNKNOWN.value)

        health_uptime = values.get('Uptime')
        health_version = values.get('BrokerVersion')
        health_store_usage = values.get('StorePercentUsage', 0)
        health_memory_usage = values.get('MemoryPercentUsage', 0)
        health_total_connections = values.get('TotalConnectionsCount', 0)
        health_total_dequeue = values.get('TotalDequeueCount', 0)
        health_total_enqueue = values.get('TotalEnqueueCount', 0)

        return_data = {
            "Uptime": health_uptime,
            "BrokerVersion": health_version,
            "Store Usage in %": health_store_usage,
            "Memory Usage in %": health_memory_usage,
            "Total Connections": health_total_connections,
            "Total Dequeue Count": health_total_dequeue,
            "Total Enqueue Count": health_total_enqueue
        }

        perfdata_values = {
            "Store Usage": SimpleNamespace(
                value=health_store_usage,
                warn="",
                crit="",
                min="",
                max=100),
            "Memory Usage": SimpleNamespace(
                value=health_memory_usage,
                warn="",
                crit="",
                min="",
                max=100),
            "Uptime": SimpleNamespace(
                value=health_uptime,
                warn="",
                crit="",
                min="",
                max=""),
            "Total Dequeue Count": SimpleNamespace(
                value=health_total_dequeue,
                warn="",
                crit="",
                min="",
                max=""),
            "Total Enqueue Count": SimpleNamespace(
                value=health_total_enqueue,
                warn="",
                crit="",
                min="",
                max=""),
        }

        return_string = self.build_string(return_data, 'Apache-MQ - OK')

        self.log.info(return_string)
        sys.exit(self.ExitCode.OK.value)

    def get_queue_status(self, broker_name, queue_name, warn=None, crit=None):
        """
        """
        exitcode = self.ExitCode.OK.value

        # Query values from activeMQ
        data = self.query_amq(self.url(broker_name, queue_name), auth=(self.user, self.password))

        # print(data)

        if len(data) == 0:
            sys.exit(self.ExitCode.UNKNOWN.value)

        status = data.get('status')

        if status != 200:
            sys.exit(self.ExitCode.CRITICAL.value)

        values = data.get('value', {})

        if len(values) == 0:
            sys.exit(self.ExitCode.UNKNOWN.value)

        summary_queue_size = 0
        return_data = []

        for _name, queue_value in values.items():
            """
            """
            if _name.startswith("org.apache.activemq"):
                """
                """
                queue_size = queue_value.get('QueueSize', 0)
                queue_producer_count = queue_value.get('ProducerCount', 0)
                queue_memory_percent_usage = queue_value.get('MemoryPercentUsage', 0)

                if queue_size > 0:
                    return_data.append({
                        str(queue_value.get('Name')): {
                            'Queue Size': queue_size,
                            #'Producer count': queue_producer_count,
                            #'Memory Usage': queue_memory_percent_usage,
                        }
                    })
                summary_queue_size += queue_size
            else:
                """
                """
                queue_size = values.get('QueueSize', 0)
                queue_producer_count = values.get('ProducerCount', 0)
                queue_memory_percent_usage = values.get('MemoryPercentUsage', 0)

                return_data.append({
                    str(values.get('Name')): {
                        'Queue Size': queue_size,
                        #'Producer count': queue_producer_count,
                        #'Memory Usage': queue_memory_percent_usage,
                    }
                })
                summary_queue_size = queue_size
                break

        # checking if Queue size exceeds warn or crit values
        if crit and crit < summary_queue_size:
            return_string_begin = "Apache-MQ - CRITICAL"
            exitcode = self.ExitCode.CRITICAL.value
        elif warn and warn < summary_queue_size:
            return_string_begin = "Apache-MQ - WARNING"
            exitcode = self.ExitCode.WARNING.value
        else:
            return_string_begin = "Apache-MQ - OK"

        return_string = self.build_string(return_data, return_string_begin)

        self.log.info(return_string)
        sys.exit(exitcode)

    def build_string(self, string_values, string_begin):
        """

        """
        return_string = string_begin + "\n"

        if isinstance(string_values, list):

            for i in string_values:
                for key, value in i.items():
                    return_string += "  %s<br>" % (key)
                    for k, v in value.items():
                        return_string += "    %s: %s<br>" % (k, v)

        if isinstance(string_values, dict):
                for key, value in string_values.items():
                    return_string += "  %s: %s<br>" % (key, value)

        return return_string

    def query_amq(self, url, auth):
        """
        """
        try:
            req = requests.get(url, auth=auth)
            req.raise_for_status()
            data = json.loads(req.text)

            return data

        except RequestException as ex:
            self.log.error(ex)
            sys.exit(self.ExitCode.CRITICAL.value)

        except ConnectionError as ex:
            self.log.error(ex)
            sys.exit(self.ExitCode.CRITICAL.value)

        except TooManyRedirects as ex:
            self.log.error(ex)
            sys.exit(self.ExitCode.CRITICAL.value)

        except Timeout as ex:
            self.log.error(ex)
            sys.exit(self.ExitCode.CRITICAL.value)

        except (RequestException, ConnectionError, URLRequired, TooManyRedirects, Timeout) as ex:
            self.log.error("Apache-MQ - CRITICAL {}".format(ex.message))
            sys.exit(self.ExitCode.CRITICAL.value)


if __name__ == '__main__':
    """
    """
    queue_name = None

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--host',
        default='localhost',
        help='Host of the Apache-MQ REST service')

    parser.add_argument(
        '--port',
        type=int,
        default=8161,
        help='Port of the Apache-MQ REST service (default: 8161)')

    parser.add_argument(
        '-u', '--username',
        default='admin',
        help='Username to be used to login')
    parser.add_argument(
        '-p',
        '--password',
        default='admin',
        help='Password to be used to login')

    parser.add_argument(
        '--check',
        required=True,
        help="'health' or 'queue'. \n With 'queue' the '--queue' parameter is required")

    parser.add_argument(
        '--broker',
        default='localhost',
        help='Brokername used to determine which broker to check. \n Defaults to localhost')

    parser.add_argument(
        '-q', '--queue',
        # required=True,
        help='Queuename which is required')

    parser.add_argument(
        '-c', '--crit',
        type=int,
        default=150,
        help='Critical Value for the Queuesize (default: 150)')

    parser.add_argument(
        '-w', '--warn',
        type=int,
        default=50,
        help='Warning Value for the Queuesize (default: 50)')

    args = parser.parse_args()

    broker = args.broker
    queue_name = args.queue
    queue_crit = args.crit
    queue_warn = args.warn

    if args.check == 'queue' and not queue_name:
        print("missing queue name (--queue)")
        parser.print_help()
        sys.exit(1)

    check = CheckApacheMQ(args.host, args.port, args.username, args.password)

    if args.check == 'queue':
        check.get_queue_status(broker, queue_name, queue_warn, queue_crit)
    elif args.check == 'health':
        check.get_health_status(broker)
    else:
        print("invalid call! not enough parameters (missing queue or health)")
        sys.exit(1)
