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
package it.polimi.chima.rest;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.util.concurrent.Futures;
import it.polimi.chima.INTutils;
import it.polimi.chima.MainComponent;
import org.onlab.packet.IPv4;
import org.onosproject.net.Device;
import org.onosproject.net.DeviceId;
import org.onosproject.net.behaviour.PiPipelineProgrammable;
import org.onosproject.net.config.NetworkConfigStore;
import org.onosproject.net.config.basics.BasicDeviceConfig;
import org.onosproject.net.device.DeviceService;
import org.onosproject.net.pi.model.*;
import org.onosproject.net.pi.service.*;
import org.onosproject.rest.AbstractWebResource;
import org.onosproject.store.service.StorageService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import javax.ws.rs.*;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import java.io.File;
import java.io.InputStream;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

import static org.onlab.util.Tools.readTreeFromStream;

//Pipeconf imports
import org.onosproject.pipelines.basic.BasicInterpreterImpl;
import org.onosproject.p4runtime.model.P4InfoParser;
import org.onosproject.p4runtime.model.P4InfoParserException;
import org.onosproject.net.behaviour.Pipeliner;
import org.onosproject.net.device.PortStatisticsDiscovery;
import org.onosproject.pipelines.basic.PortStatisticsDiscoveryImpl;
import org.onosproject.pipelines.basic.BasicPipelinerImpl;

import static org.onosproject.net.pi.model.PiPipeconf.ExtensionType.BMV2_JSON;
import static org.onosproject.net.pi.model.PiPipeconf.ExtensionType.P4_INFO_TEXT;

import org.onosproject.net.flow.FlowRuleProgrammable;

/**
 * Pipeconf installation management.
 */
@Path("pipeconf")
public class PipeconfWebResource extends AbstractWebResource {

    private final Logger log = LoggerFactory.getLogger(getClass());

    /*
    *   Taken from
    *   https://github.com/opennetworkinglab/onos/blob/2b4de873e4033b7973b399d25cb8828a73bc2e24/pipelines/basic/src/main/java/org/onosproject/pipelines/basic/PipeconfLoader.java#L118-L124
    */
    private static PiPipelineModel parseP4Info(URL p4InfoUrl) {
        try {
            return P4InfoParser.parse(p4InfoUrl);
        } catch (P4InfoParserException e) {
            throw new IllegalStateException(e);
        }
    }

    /**
     * Install pipeconf on the specified device
     *
     * @param arguments JSON collection of the data needed to identify the pipeconf
     * @return 200 OK
     * @return 400 Bad Request
     */
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    public Response installPipeline(InputStream arguments) {
        /* Example post parameter
            {
                "deviceID" : "device:bmv2:s22",
                "json": "/p4c-out/bmv2/basic.json",
                "p4info": "/p4c-out/bmv2/basic_p4info.txt"
            }
         */
        try {
            //Read parameters from JSON
            ObjectNode body = readTreeFromStream(mapper(), arguments);
            JsonNode deviceIdNode = body.path("deviceID");
            JsonNode jsonNode = body.path("json");
            JsonNode p4infoNode = body.path("p4info");

            if(deviceIdNode.isMissingNode() || jsonNode.isMissingNode() || p4infoNode.isMissingNode())
                return Response.status(Response.Status.BAD_REQUEST).build();

            DeviceService deviceService = get(DeviceService.class);
            DeviceId deviceId = DeviceId.deviceId(deviceIdNode.asText());
            Device device = deviceService.getDevice(deviceId);
            if(device == null)
            {
                return Response.status(Response.Status.BAD_REQUEST).build();
            }

            final URL jsonUrl = new File(jsonNode.asText()).toURI().toURL();
            final URL p4InfoUrl = new File(p4infoNode.asText()).toURI().toURL();

            //Create pipeconf
            PiPipeconfId pipeId = new PiPipeconfId("it.polimi.chima."+deviceId.toString());
            PiPipeconf pipeconf = DefaultPiPipeconf.builder()
                    .withId(pipeId)
                    .withPipelineModel(parseP4Info(p4InfoUrl))
                    .addBehaviour(PiPipelineInterpreter.class, BasicInterpreterImpl.class)
                    .addBehaviour(Pipeliner.class, BasicPipelinerImpl.class)
                    .addBehaviour(PortStatisticsDiscovery.class, PortStatisticsDiscoveryImpl.class)
                    .addExtension(P4_INFO_TEXT, p4InfoUrl)
                    .addExtension(BMV2_JSON, jsonUrl)
                    .build();

            //Get needed services
            PiPipeconfMappingStore pipeconfMappingStore = get(PiPipeconfMappingStore.class);
            PiPipeconfService pipeconfService = get(PiPipeconfService.class);
            PiPipeconfWatchdogService watchdogService = get(PiPipeconfWatchdogService.class);
            MainComponent component = MainComponent.getInstance();

            boolean result = false;

            //Check if a pipeconf with the same name is already registered
            if(!pipeconfService.getPipeconf(pipeId).isPresent())
            {
                //Register pipeconf
                pipeconfService.register(pipeconf);

                //Update the pipeconf in the device configuration
                NetworkConfigStore netconfStore = get(NetworkConfigStore.class);
                BasicDeviceConfig conf = netconfStore.getConfig(deviceId, BasicDeviceConfig.class);
                conf = conf.pipeconf(pipeId.toString());
                netconfStore.applyConfig(deviceId, BasicDeviceConfig.class, conf.node());
                log.info("Device configuration modified with "+conf.pipeconf());

                //Bind pipeconf to the device and let ONOS install it
                pipeconfMappingStore.createOrUpdateBinding(deviceId, pipeId);
                //Trigger a check to make ONOS process the change
                watchdogService.triggerProbe(deviceId);

                //Set the status in the map to "not ready"
                //The event listener in MainComponent will set the status to true
                component.deviceReadyMap.put(deviceId, false);

                //Assume everything works ¯\_(ツ)_/¯
                result = true;

                log.info("Registered new pipeconf");
            }
            else
            {
                //TODO: remeber this solution may leave the dataplane unusable for some time
                //Register pipeconf
                pipeconfService.unregister(pipeId);
                pipeconfService.register(pipeconf);

                //Trigger a check to make ONOS process the change
                watchdogService.triggerProbe(deviceId);

                //Set the status in the map to "not ready"
                //The event listener in MainComponent will set the status to true
                component.deviceReadyMap.put(deviceId, false);

                //Assume everything works ¯\_(ツ)_/¯
                result = true;

                log.info("Registered new pipeconf");
            }

            ObjectNode node = mapper().createObjectNode().put("result", result ? 1 : 0);
            return ok(node).build();
        }
        catch (Exception ex)
        {
            log.info("Error", ex);
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(ex.toString()).build();
        }
    }

    /**
     * Check if the pipeconf is ready on the specified device
     *
     * @param arguments JSON that only describes the device to check
     * @return 200 OK
     * @return 400 Bad Request
     */
    @POST
    @Path("check")
    @Consumes(MediaType.APPLICATION_JSON)
    public Response checkPipeline(InputStream arguments) {
        /* Example post parameter
            {
                "deviceID" : "device:bmv2:s22"
            }
         */

        try{
            //Read parameters from JSON
            ObjectNode body = readTreeFromStream(mapper(), arguments);
            JsonNode deviceIdNode = body.path("deviceID");

            if(deviceIdNode.isMissingNode())
                return Response.status(Response.Status.BAD_REQUEST).build();

            DeviceService deviceService = get(DeviceService.class);
            DeviceId deviceId = DeviceId.deviceId(deviceIdNode.asText());
            Device device = deviceService.getDevice(deviceId);
            if(device == null)
            {
                return Response.status(Response.Status.BAD_REQUEST).build();
            }

            MainComponent component = MainComponent.getInstance();
            boolean ready = false;
            if(component.deviceReadyMap.containsKey(deviceId)){
                ready = component.deviceReadyMap.get(deviceId);
            }

            ObjectNode node = mapper().createObjectNode().put("ready", ready ? 1 : 0);
            return ok(node).build();
        }
        catch(Exception ex) {
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(ex.toString()).build();
        }
    }
}
