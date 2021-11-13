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
import org.onlab.packet.IPv4;
import org.onosproject.inbandtelemetry.api.IntIntentId;
import org.onosproject.inbandtelemetry.api.IntService;
import org.onosproject.net.intent.IntentId;
import org.onosproject.rest.AbstractWebResource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import static org.onlab.util.Tools.readTreeFromStream;
import it.polimi.chima.INTutils;

import javax.ws.rs.*;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import java.io.InputStream;
import java.util.ArrayList;

/**
 * INT intents management.
 */
@Path("int")
public class INTWebResource extends AbstractWebResource {
    private final Logger log = LoggerFactory.getLogger(getClass());

    /////////////////////////////////////////////////////////////////////////////////////// Management of INT intents
    /**
     * Create an INT intent
     *
     * @param intent JSON description of the intent to create
     * @return 200 OK
     * @return 400 Bad Request
     */
    @POST
    @Consumes(MediaType.APPLICATION_JSON)
    public Response addIntent(InputStream intent) {
        /* Example post parameter
            {
                "srcIP": "10.0.0.0/24",
                "dstIP": "10.0.0.0/24"
            }
         */
        try {
            IntService intService = get(IntService.class);
            ObjectNode body = readTreeFromStream(mapper(), intent);

            JsonNode srcIP = body.path("srcIP");
            JsonNode dstIP = body.path("dstIP");

            if(srcIP.isMissingNode() || dstIP.isMissingNode())
                return Response.status(Response.Status.BAD_REQUEST).build();

            byte IPproto = 0;
            switch(body.path("proto").asText(""))
            {
                case "UDP":
                    IPproto = IPv4.PROTOCOL_UDP;
                    break;
                case "TCP":
                    IPproto = IPv4.PROTOCOL_TCP;
            }

            int srcPort = body.path("srcPort").asInt(0);
            int dstPort = body.path("dstPort").asInt(0);

            log.info("Adding intent from "+srcIP.asText()+" to "+dstIP.asText());

            //Stores the list of IDs of the intents used to implement the behavior
            ArrayList<IntIntentId> results = new ArrayList<>();
            results.add( INTutils.addIntent(srcIP.asText(), dstIP.asText(), IPproto, srcPort, dstPort, intService) );

            ObjectNode root = mapper().createObjectNode();
            ArrayNode ids = root.putArray("intentID");
            for(IntIntentId id : results)
                ids.add(id.toString());

            return ok(root).build();
        }
        catch (Exception ex)
        {
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(ex.toString()).build();
        }
    }

    /**
     * Remove an INT intent
     *
     * @param id ID of the intent to remove
     * @return 200 OK
     */
    @DELETE
    @Path("{id}")
    @Consumes(MediaType.APPLICATION_JSON)
    public Response removeIntent(@PathParam("id") long id) {
        try {
            IntService intService = get(IntService.class);

            log.info("Removing intent with ID " + id);
            INTutils.removeIntent(id, intService);

            ObjectNode node = mapper().createObjectNode().put("intentID", id);
            return ok(node).build();
        }
        catch (Exception ex)
        {
            return Response.status(Response.Status.INTERNAL_SERVER_ERROR).entity(ex.toString()).build();
        }
    }
}
