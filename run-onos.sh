#!/usr/bin/bash

cd $ONOS_ROOT
ONOS_APPS=gui2,drivers.bmv2,proxyarp,lldpprovider,hostprovider,fwd,inbandtelemetry bazel run onos-local -- clean debug