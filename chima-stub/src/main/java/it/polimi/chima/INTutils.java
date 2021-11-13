package it.polimi.chima;

import org.onlab.packet.*;
import org.onosproject.inbandtelemetry.api.IntIntent;
import org.onosproject.inbandtelemetry.api.IntIntentId;
import org.onosproject.inbandtelemetry.api.IntService;
import org.onosproject.net.behaviour.inbandtelemetry.IntMetadataType;
import org.onosproject.net.flow.DefaultTrafficSelector;
import org.onosproject.net.flow.TrafficSelector;
import org.osgi.service.component.annotations.Reference;
import org.osgi.service.component.annotations.ReferenceCardinality;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/*
    Class of static methods to easily interface with IntService from the
    inbandtelemetry app
 */
public class INTutils {
    private final static Logger log = LoggerFactory.getLogger(INTutils.class);

    /*
        Taken from
        https://github.com/opennetworkinglab/onos/blob/219dd8fedf54e33da8df7bcb4e755724a7637650/apps/inbandtelemetry/app/src/main/java/org/onosproject/inbandtelemetry/app/ui/IntAppUiMessageHandler.java#L177
    */
    private static Ip4Prefix parseIp4Prefix(String prefixString) {
        if (prefixString == null) {
            return null;
        }
        String[] splitString = prefixString.split("/");
        Ip4Address ip4Address = Ip4Address.valueOf(splitString[0]);
        int mask = splitString.length > 1 ? Integer.parseInt(splitString[1]) : 32;
        return Ip4Prefix.valueOf(ip4Address, mask);
    }

    public static IntIntentId addIntent(String srcIP, String dstIP, byte IPproto, int srcPort, int dstPort, IntService intService)
    {
        TrafficSelector.Builder trafficSelector = DefaultTrafficSelector.builder();
        IntIntent.Builder builder = IntIntent.builder();

        try {
            //Flow selection
            trafficSelector.matchIPSrc(parseIp4Prefix(srcIP));
            trafficSelector.matchIPDst(parseIp4Prefix(dstIP));
            switch(IPproto)
            {
                case IPv4.PROTOCOL_TCP:
                {
                    trafficSelector.matchIPProtocol(IPproto);
                    if(srcPort != 0) trafficSelector.matchTcpSrc(TpPort.tpPort(srcPort));
                    if(dstPort != 0) trafficSelector.matchTcpDst(TpPort.tpPort(dstPort));
                    break;
                }
                case IPv4.PROTOCOL_UDP:
                {
                    trafficSelector.matchIPProtocol(IPproto);
                    if(srcPort != 0) trafficSelector.matchUdpSrc(TpPort.tpPort(srcPort));
                    if(dstPort != 0) trafficSelector.matchUdpDst(TpPort.tpPort(dstPort));
                    break;
                }
                case 0:
                    break;
                default:
                    trafficSelector.matchIPProtocol(IPproto);
                    break;
            }

            builder.withSelector(trafficSelector.build());

            //Metadata
            builder.withMetadataType(IntMetadataType.SWITCH_ID)
                    .withMetadataType(IntMetadataType.INGRESS_TIMESTAMP)
                    .withMetadataType(IntMetadataType.EGRESS_TIMESTAMP);

            //Fixed values
            builder.withHeaderType(IntIntent.IntHeaderType.HOP_BY_HOP)
                    .withReportType(IntIntent.IntReportType.TRACKED_FLOW)
                    .withTelemetryMode(IntIntent.TelemetryMode.INBAND_TELEMETRY) /*Only use embedded*/;

            if(intService == null)
                log.error("intService missing");

            return intService.installIntIntent(builder.build());
        }
        catch(Exception ex)
        {
            log.error(ex.toString());
            return null;
        }
    }

    public static void removeIntent(long id, IntService intService)
    {
        intService.removeIntIntent(IntIntentId.valueOf(id));
    }
}
