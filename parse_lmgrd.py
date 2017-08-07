#!/usr/bin/env python
# The script to parse a lmgrd log and give some license usage metrics
# 
# Copyright (c) 2014 Grigory Rechistov <grigory.rechistov@phystech.edu>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, 
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, 
# this list of conditions and the following disclaimer in the documentation 
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, 
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import sys
import re

def main():
    lines = []
    try:
        with open (sys.argv[1], "r") as inp:
            lines=inp.readlines()
    except IOError as e:
        print e
        print "Usage: %s logfile" % sys.argv[0]
        return 1
    vendors = set()
    hosts = set()
    features = set()
    #ins  = dict() # TODO: count IN records too.
    unsupported = set()
    
    outs = dict()
    for l in lines:
        # Look for lines like this:
        # 15:13:02 (simics) OUT: "x86-nehalem" proskin@lucy  (8 licenses) 
        # 15:20:27 (simics) IN: "simics" proskin@lucy  
        #print ">>> %s" % l
        m = re.search(r'\((\w+)\)\s+OUT:\s+"(.+)"\s+([^\s]+@[^\s]+)', l)
        if m:
            vendor  = m.group(1)
            feature = m.group(2)
            user    = m.group(3).split("@")[0]
            host    = m.group(3).split("@")[1]
            # Now try to get how many licenses has been acquired
            m = re.search(r'\((\d+)\s+licenses\)', l)
            if m: n_lic = int(m.group(1))
            else: n_lic = 1
            #print ">>> OUT vendor = %s, feature = %s, n_lic = %d, user = %s, host = %s" %\
                #(vendor, feature, n_lic, user, host)
            vendors.add(vendor)
            hosts.add(host)
            features.add(feature)
            if not (user in outs):
                outs[user] = dict()
            if not (feature in outs[user]):
                outs[user][feature] = n_lic
            else:
                outs[user][feature] = outs[user][feature] + n_lic
        # Look for requests of UNSUPPORTED features.
        m = re.search(r'\((\w+)\)\s+UNSUPPORTED:\s+"(.+)"\s+.*([^\s]+@[^\s]+)', l)
        if m:
            vendor  = m.group(1)
            feature = m.group(2)
            user    = m.group(3).split("@")[0]
            host    = m.group(3).split("@")[1]
            print ">>> UNSUPPORTED vendor = %s, feature = %s, n_lic = %d, user = %s, host = %s" %\
                (vendor, feature, n_lic, user, host)
            unsupported.add(feature)

    # Dump stats
    print "All vendors:  ", [l for l in vendors]
    print "All hosts:    ", [l for l in hosts]
    print "All features: ", [l for l in features]
    print "All users:    ", outs.keys()
    
    # Users and features they've checked out, in total
    for u in outs.keys():
        print "User %s total checkouts:" % u
        for f in outs[u].keys():
            print "{:<32} {:>5}".format(f, outs[u][f])
        print ""

    if len(unsupported) != 0:
        print "Requested unsupported features:", [l for l in unsupported]
    return 0
        
if __name__ == "__main__":
    main()