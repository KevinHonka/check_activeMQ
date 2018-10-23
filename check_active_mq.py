#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import json
from pprint import pprint
from urllib2 import HTTPError

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

    def get_stats(self):

        amq_path = "read/org.apache.activemq:type=Broker,brokerName=localhost"

        try:
            req = requests.get(self.host + amq_path, auth=(self.user, self.password))
            req.raise_for_status()
            self.data = json.loads(req.text)

        except (RequestException, ConnectionError, HTTPError, URLRequired, TooManyRedirects, Timeout) as ex:
            self.log.error("Apache-MQ - CRITICAL {}".format(ex.message))
            sys.exit(self.ExitCode.CRITICAL.value)

    def print_status(self):
        return_String = "Apache-MQ - OK "
        return_String += " Uptime: %s \n" % self.data['value']['Uptime']
        return_String += " BrokerVersion: %s \n" % self.data['value']['BrokerVersion']
        return_String += " Store Usage: %s \n" % self.data['value']['StorePercentUsage']
        return_String += " Memory Usage: %s \n" % self.data['value']['MemoryPercentUsage']
        return_String += " Total Connections: %s \n" % self.data['value']['TotalConnectionsCount']
        return_String += " Total Dequeue Count: %s \n" % self.data['value']['TotalDequeueCount']
        return_String += " Total Enqueue Count: %s \n" % self.data['value']['TotalEnqueueCount']

        return_String += "|"
        return_String += " {}={};{};{};{};{}".format("Store Usage", self.data['value']['StorePercentUsage'], "", "", "", 100)
        return_String += " {}={};{};{};{};{}".format("Memory Usage", self.data['value']['MemoryPercentUsage'], "", "", "", 100)

        self.log.info(return_String)
        sys.exit(self.ExitCode.OK.value)

    def get_queue_status(self, broker_name, queue_name):

        amq_path = "read/org.apache.activemq:type=Broker,brokerName={},destinationType=Queue,destinationName={}".format(broker_name, queue_name)

        try:
            req = requests.get(self.host + amq_path, auth=(self.user, self.password))
            req.raise_for_status()
            self.data = json.loads(req.text)

            pprint(self.data)

        except (RequestException, ConnectionError, HTTPError, URLRequired, TooManyRedirects, Timeout) as ex:
            self.log.error("Apache-MQ - CRITICAL {}".format(ex.message))
            sys.exit(self.ExitCode.CRITICAL.value)


if __name__ == '__main__':
    check = CheckApacheMQ()

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument('--host', default='http://localhost:8161/api/jolokia/', help='Host of the Apache-MQ REST service')
    parser.add_argument('-u', '--username', default='admin', help='Username to be used to login')
    parser.add_argument('-p', '--password', default='admin', help='Password to be used to login')

    subparsers = parser.add_subparsers(dest='command')

    queueu_parser = subparsers.add_parser('queue')
    queueu_parser.add_argument('-b', '--broker', default='localhost', help='Brokername used to determine which broker to check. \n Defaults to localhost')
    queueu_parser.add_argument('-q', '--queue', required=True, help='Queuename which is needed')
    health_parser = subparsers.add_parser('health')

    args = parser.parse_args()

    check.user = args.username
    check.password = args.password
    check.host = args.host

    print(args.command)

    if args.command == 'queue':
        check.get_queue_status(args.broker, args.queue)
    elif args.command == 'health':
        check.get_stats()
        check.print_status()
