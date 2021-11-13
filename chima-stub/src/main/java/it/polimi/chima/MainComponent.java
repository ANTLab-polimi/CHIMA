/*
 * Copyright 2021-present Open Networking Foundation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package it.polimi.chima;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.Maps;
import org.onlab.packet.IpAddress;
import org.onosproject.mastership.MastershipService;
import org.onosproject.net.*;
import org.onosproject.net.device.*;
import org.onosproject.net.flow.*;
import org.onosproject.net.flow.impl.FlowRuleDriverProvider;
import org.onosproject.net.flow.impl.FlowRuleManager;
import org.onosproject.net.host.HostEvent;
import org.onosproject.net.host.HostListener;
import org.onosproject.net.host.HostService;
import org.onosproject.net.link.*;
import org.onosproject.net.pi.service.PiPipeconfWatchdogEvent;
import org.onosproject.net.pi.service.PiPipeconfWatchdogListener;
import org.onosproject.net.pi.service.PiPipeconfWatchdogService;
import org.osgi.service.component.annotations.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.net.*;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.HashSet;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

import org.onosproject.net.flow.FlowRuleProviderService;

/**
 * Implementation of the basic functionality of the FM stub
 */
@Component(immediate = true)
public class MainComponent {

    private final Logger log = LoggerFactory.getLogger(getClass());

    ObjectMapper jsonMapper;

    //////////////////////////////////////////Singleton
    private static MainComponent instance;
    public static MainComponent getInstance()
    {
        return instance;
    }


    ////////////////////////////////////////Methods called by the REST API
    private Set<Integer> appsPorts;

    public Set<Integer> getApplications()
    {
        return appsPorts;
    }

    public boolean addApplication(int port)
    {
        appsPorts.add(port);
        log.info("Current apps: "+appsPorts.toString());

        //Send initial topology information
        for(Device d : deviceService.getAvailableDevices())
        {
            sendEvent(deviceJson(d, null), "/device");
            for(Port p : deviceService.getPorts(d.id()))
            {
                sendEvent(portJson(d,p,null), "/port");
            }
            for(Host h : hostService.getConnectedHosts(d.id()))
            {
                if(!h.ipAddresses().isEmpty())
                    sendEvent(hostJson(h,null), "/host");
            }
        }
        for(Link l : linkService.getActiveLinks())
        {
            sendEvent(linkJson(l, null), "/link");
        }

        return true;
    }

    public boolean removeApplication(int port)
    {
        appsPorts.remove(port);
        log.info("Current apps: "+appsPorts.toString());
        return true;
    }

    /////////////////////////////////////////Serializers
    private String deviceJson(Device d, DeviceEvent.Type event)
    {
        ObjectNode data = jsonMapper.createObjectNode();
        data.put("id", d.id().toString());
        if(event != null)
        {
            switch (event)
            {
                case DEVICE_ADDED: {
                    data.put("available", "YES");
                    break;
                }
                case DEVICE_REMOVED: {
                    data.put("available", "NO");
                    break;
                }
                default: {
                    data.put("available", deviceService.isAvailable(d.id()) ? "YES" : "NO" );
                }
            }
        }
        else
            data.put("available", deviceService.isAvailable(d.id()) ? "YES" : "NO" );

        return toJson(data);
    }

    private String portJson(Device d, Port p, DeviceEvent.Type event)
    {
        ObjectNode data = jsonMapper.createObjectNode();
        data.put("id", d.id().toString());
        data.put("number", p.number().toLong());
        data.put("speed", p.portSpeed());
        data.put("name", p.annotations().value("portName"));
        data.put("mac", p.annotations().value("portMac"));

        if(event != null)
        {
            switch (event)
            {
                case PORT_ADDED: {
                    data.put("enabled", "YES");
                    break;
                }
                case PORT_REMOVED: {
                    data.put("enabled", "NO");
                    break;
                }
                default: {
                    data.put("enabled", p.isEnabled() ? "YES" : "NO");
                }
            }
        }
        else
            data.put("enabled", p.isEnabled() ? "YES" : "NO");

        return toJson(data);
    }

    private String linkJson(Link l, LinkEvent.Type event)
    {
        ObjectNode data = jsonMapper.createObjectNode();
        data.put("srcDev", l.src().deviceId().toString());
        data.put("srcPort", l.src().port().toLong());
        data.put("dstDev", l.dst().deviceId().toString());
        data.put("dstPort", l.dst().port().toLong());

        if(event != null)
        {
            switch (event)
            {
                case LINK_ADDED: {
                    data.put("state", "ACTIVE");
                    break;
                }
                case LINK_REMOVED: {
                    data.put("state", "INACTIVE");
                    break;
                }
                default: {
                    data.put("state", l.state().toString());
                }
            }
        }
        else
            data.put("state", l.state().toString());

        return toJson(data);
    }

    private String hostJson(Host h, HostEvent.Type event)
    {
        ObjectNode data = jsonMapper.createObjectNode();
        data.put("mac", h.mac().toString());
        ArrayNode ips = data.putArray("ip");
        for(IpAddress ip : h.ipAddresses())
        {
            ips.add(ip.toString());
        }
        String[] location = h.location().toString().split("/");
        data.put("device", location[0]);
        data.put("port", Long.valueOf(location[1]));

        if(event != null)
        {
            switch (event)
            {
                case HOST_ADDED: {
                    data.put("available", "YES");
                    break;
                }
                case HOST_REMOVED: {
                    data.put("available", "NO");
                    break;
                }
                default: {
                    //Even if this is false it will be discarded when
                    //it will be polled
                    data.put("available", "YES");
                }
            }
        }
        else {
            //Even if this is false it will be discarded when
            //it will be polled
            data.put("available", "YES");
        }

        return toJson(data);
    }

    ////////////////////////////////////////Event listeners
    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    protected DeviceService deviceService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    protected LinkService linkService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    protected HostService hostService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    protected PiPipeconfWatchdogService watchdogService;

    @Reference(cardinality = ReferenceCardinality.MANDATORY)
    protected FlowRuleService flowRuleService;

    private DeviceListener devL = new DeviceListener() {
        @java.lang.Override
        public void event(DeviceEvent event) {
            if(event.type() == DeviceEvent.Type.PORT_STATS_UPDATED)
                return; //Regular event, not interesting

            //log.info("(D) Event type = "+event.type());

            String data = null;
            String path = null;

            if(event.port() != null) {
                data = portJson(event.subject(), event.port(), event.type());
                path = "/port";
            }
            else {
                data = deviceJson(event.subject(), event.type());
                path = "/device";
            }

            //log.info(data);
            String finalData = data;
            String finalPath = path;
            sendEvent(finalData, finalPath);

            //log.info(event.toString());
        }
    };

    private LinkListener linkL = new LinkListener() {
        @Override
        public void event(LinkEvent event) {
            //log.info("(L) Event type = "+event.type());

            String data = linkJson(event.subject(), event.type());
            //log.info(data);
            sendEvent(data, "/link");

            //log.info(event.toString());
        }
    };

    private HostListener hostL = new HostListener() {
        @Override
        public void event(HostEvent event) {
            //If there is no IP we would not know how to contact the host
            if(!event.subject().ipAddresses().isEmpty())
            {
                //log.info("(H) Event type = "+event.type());

                String data = hostJson(event.subject(), event.type());
                //log.info(data);
                sendEvent(data, "/host");

                //log.info(event.toString());
            }
        }
    };

    public Map<DeviceId, Boolean> deviceReadyMap = new ConcurrentHashMap<DeviceId, Boolean>();
    private PiPipeconfWatchdogListener pipeconfListener = new PiPipeconfWatchdogListener() {
        @Override
        public void event(PiPipeconfWatchdogEvent event) {
            if(event.type() == PiPipeconfWatchdogEvent.Type.PIPELINE_CHANGED)
            {
                DeviceId deviceId = event.subject();
                Device device = deviceService.getDevice(deviceId);

                FlowRuleManager manager = (FlowRuleManager) flowRuleService;
                manager.driverProvider.pollDeviceFlowEntries(device);

                deviceReadyMap.put(event.subject(), true);
            }
        }
    };

    /////////////////////////////////////////////////////////////////Utils
    private String toJson(Object o)
    {
        try{
            return jsonMapper.writeValueAsString(o);
        }
        catch(Exception ex)
        {
            return ex.getMessage() + ": " + o.toString();
        }
    }

    private boolean sendEvent(String e, String path) {
        HttpClient client = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .build();
        HttpRequest request = null;
        for (int port : appsPorts) {
            try {
                 request = HttpRequest.newBuilder()
                        .POST(HttpRequest.BodyPublishers.ofString(e))
                        .uri(URI.create("http://localhost:"+port+"/update"+path))
                        .header("Content-Type", "application/json")
                        .build();

                 client.send(request, HttpResponse.BodyHandlers.discarding());
            }
            catch(ConnectException ex)
            {
                log.error("Connection exception: "+ex.toString());
                appsPorts.remove(port);
            }
            catch(Exception ex)
            {
                log.error("Send event error: " + ex.toString());
                return false;
            }
        }

        return true;
    }

    ////////////////////////////////////////////////////Lifecycle functions
    @Activate
    protected void activate() {
        instance = this;

        appsPorts = new HashSet<>();
        jsonMapper = new ObjectMapper();

        deviceService.addListener(devL);
        linkService.addListener(linkL);
        hostService.addListener(hostL);
        watchdogService.addListener(pipeconfListener);

        log.info("CHIMA stub started");
    }

    @Deactivate
    protected void deactivate() {
        instance = null;

        deviceService.removeListener(devL);
        linkService.removeListener(linkL);
        hostService.removeListener(hostL);
        watchdogService.removeListener(pipeconfListener);

        log.info("CHIMA stub stopped");
    }
}
