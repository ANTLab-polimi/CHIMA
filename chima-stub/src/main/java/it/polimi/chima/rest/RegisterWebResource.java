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

import com.fasterxml.jackson.databind.node.ObjectNode;
import it.polimi.chima.MainComponent;
import org.onosproject.net.device.DeviceService;
import org.onosproject.rest.AbstractWebResource;

import javax.ws.rs.Consumes;
import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.DELETE;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Events notifications management.
 */
@Path("register")
public class RegisterWebResource extends AbstractWebResource {
    private final Logger log = LoggerFactory.getLogger(getClass());

    /////////////////////////////////////////////////////////////////// Management of subscribed applications
    /**
     * Get a list of currently registered applications.
     *
     * @return 200 OK
     */
    @GET
    @Consumes(MediaType.APPLICATION_JSON)
    public Response checkApp() {
        MainComponent component = MainComponent.getInstance();
        component.getApplications();

        try {
            return ok(mapper().writeValueAsString(component.getApplications())).build();
        }
        catch(Exception ex)
        {
            log.error(ex.toString());
            return null;
        }
    }

    /**
     * Register application to receive events.
     *
     * @param port TCP port of the application REST API
     * @return 200 OK
     */
    @POST
    @Path("{port}")
    @Consumes(MediaType.APPLICATION_JSON)
    public Response registerApp(@PathParam("port") int port) {
        MainComponent component = MainComponent.getInstance();
        component.addApplication(port);
        log.info("Application registered on port "+port);

        ObjectNode node = mapper().createObjectNode().put("result", port);
        return ok(node).build();
    }

    /**
     * Remove application so that it no longer to receives events.
     *
     * @param port TCP port of the application REST API
     * @return 200 OK
     */
    @DELETE
    @Path("{port}")
    @Consumes(MediaType.APPLICATION_JSON)
    public Response removeApp(@PathParam("port") int port) {
        MainComponent component = MainComponent.getInstance();
        component.removeApplication(port);
        log.info("Application removed on port "+port);

        ObjectNode node = mapper().createObjectNode().put("removed", port);
        return ok(node).build();
    }
}
