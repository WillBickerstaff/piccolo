import os, subprocess, re, time, sys
from threading import Thread

class TestNet(Thread):
    lifeline = re.compile(r"(\d) received")
    report = ("No Response", "Partial Response", "Alive")

    def __init__(self, ip):
        Thread.__init__(self)
        self.ip = ip
        self.status = -1
        self.mac = None

    def run(self):
        host = subprocess.Popen(["ping", "-q", "-c2", self.ip],
                                stdout=subprocess.PIPE)
        line = host.communicate()[0]
        res = re.findall(TestNet.lifeline, line)
        if res:
            self.status = int(res[0])
        if self.status == 2:
            pid = subprocess.Popen(["arp", "-n", self.ip],
                                   stdout=subprocess.PIPE)
            s = pid.communicate()[0]
            self.mac = re.search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})",
                                 s).groups()[0]
def testloc():
    hostlist = []
    liveips = []
    for host in range(1, 254):
        ip = "192.168.1.%d"%host
        cur = TestNet(ip)
        hostlist.append(cur)
        cur.start()

    for host in hostlist:
        host.join()
        if host.status == 2: liveips.append(host)
    
    for host in liveips:
        print host.ip, host.mac
testloc()
