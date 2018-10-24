#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import json
from pprint import pprint
from types import SimpleNamespace

import requests
import sys

from enum import Enum
import logging
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

    @property
    def user(self):
        return self.__user

    @user.setter
    def user(self, user):
        if user is not None:
            self.__user = user
        else:
            raise ValueError()

    @property
    def password(self):
        return self.__password

    @password.setter
    def password(self, password):
        if password is not None:
            self.__password = password
        else:
            raise ValueError()

    @property
    def host(self):
        return self.__host

    @host.setter
    def host(self, host):
        if host is not None:
            self.__host = host
        else:
            raise ValueError()

    def __init__(self, ):
        self.__url = None
        self.__user = None
        self.__password = None

        self.log = logging.getLogger('CheckApacheMQ')
        streamhandler = logging.StreamHandler(sys.stdout)
        self.log.addHandler(streamhandler)
        self.log.setLevel(logging.INFO)

    def get_health_status(self):

        amq_path = "read/org.apache.activemq:type=Broker,brokerName=localhost"

        data = self.query_amq(self.host + amq_path, auth=(self.user, self.password))

        return_String = "Apache-MQ - OK "
        return_String += " Uptime: %s \n" % data['value']['Uptime']
        return_String += " BrokerVersion: %s \n" % data['value']['BrokerVersion']
        return_String += " Store Usage: %s \n" % data['value']['StorePercentUsage']
        return_String += " Memory Usage: %s \n" % data['value']['MemoryPercentUsage']
        return_String += " Total Connections: %s \n" % data['value']['TotalConnectionsCount']
        return_String += " Total Dequeue Count: %s \n" % data['value']['TotalDequeueCount']
        return_String += " Total Enqueue Count: %s \n" % data['value']['TotalEnqueueCount']

        return_String += "|"
        return_String += " {}={};{};{};{};{}".format("Store Usage", data['value']['StorePercentUsage'], "", "", "", 100)
        return_String += " {}={};{};{};{};{}".format("Memory Usage", data['value']['MemoryPercentUsage'], "", "", "",
                                                     100)

        self.log.info(return_String)
        sys.exit(self.ExitCode.OK.value)

    def get_queue_status(self, broker_name, queue_name, warn=None, crit=None):

        exitcode = self.ExitCode.OK.value

        amq_path = "read/org.apache.activemq:type=Broker,brokerName={},destinationType=Queue,destinationName={}".format(
            broker_name, queue_name)

        # Query values from activeMQ
        data = self.query_amq(self.host + amq_path, auth=(self.user, self.password))

        # Building dicts to better build strings
        return_data = {
            'Queue Size': data['value']['QueueSize'],
            'Producer count': data['value']['ProducerCount'],
            'Memory Usage': data['value']['MemoryPercentUsage'],
        }

        perfdata_values = {
            "Store Usage": SimpleNamespace(value=data['value']['MemoryUsageByteCount'],
                                           warn="",
                                           crit="",
                                           min="",
                                           max=data['value']['MemoryLimit'])
        }

        # checking if Queue size exceeds warn or crit values
        if crit and crit < data['value']['QueueSize']:
            return_string_begin = "Apache-MQ - CRITICAL "
            exitcode = self.ExitCode.CRITICAL.value
        elif warn and warn < data['value']['QueueSize']:
            return_string_begin = "Apache-MQ - WARNING "
            exitcode = self.ExitCode.WARNING.value
        else:
            return_string_begin = "Apache-MQ - OK "

        return_string = self.build_string(return_data, return_string_begin)

        return_string += self.build_perfdata(perfdata_values)

        self.log.info(return_string)
        sys.exit(exitcode)

    def build_perfdata(self, perfdata_values):
        perfdata_string = " |"

        for key, values in perfdata_values.items():
            perfdata_string += " {}={};{};{};{};{}".format(key, values.value, values.warn, values.crit, values.min,
                                                           values.max)

        return perfdata_string

    def build_string(self, string_values, string_begin="Apache-MQ - OK "):
        return_string = string_begin

        for key, value in string_values.items():
            return_string += " {}: {} \n".format(key, value)

        return return_string

    def query_amq(self, url, auth):
        try:
            req = requests.get(url, auth=auth)
            req.raise_for_status()
            data = json.loads(req.text)

            return data

        except (RequestException, ConnectionError, URLRequired, TooManyRedirects, Timeout) as ex:
            self.log.error("Apache-MQ - CRITICAL {}".format(ex.message))
            sys.exit(self.ExitCode.CRITICAL.value)


if __name__ == '__main__':
    check = CheckApacheMQ()

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('--host', default='http://localhost:8161/api/jolokia/',
                        help='Host of the Apache-MQ REST service')
    parser.add_argument('-u', '--username', default='admin', help='Username to be used to login')
    parser.add_argument('-p', '--password', default='admin', help='Password to be used to login')

    subparsers = parser.add_subparsers(dest='command')

    queueu_parser = subparsers.add_parser('queue')
    queueu_parser.add_argument('-b', '--broker', default='localhost',
                               help='Brokername used to determine which broker to check. \n Defaults to localhost')
    queueu_parser.add_argument('-q', '--queue', required=True, help='Queuename which is needed')
    queueu_parser.add_argument('-c', '--crit', default=500, help='Critical Value for the Queuesize')
    queueu_parser.add_argument('-w', '--warn', default=250, help='Warning Value for the Queuesize')

    health_parser = subparsers.add_parser('health')

    args = parser.parse_args()

    check.user = args.username
    check.password = args.password
    check.host = args.host

    print(args.command)

    if args.command == 'queue':
        check.get_queue_status(args.broker, args.queue, args.warn, args.crit)
    elif args.command == 'health':
        check.get_stats()
        check.print_status()
