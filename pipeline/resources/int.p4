/*
 * Copyright 2017-present Open Networking Foundation
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

/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

#include "include/defines.p4"
#include "include/headers.p4"
#include "include/actions.p4"
#include "include/int_definitions.p4"
#include "include/int_headers.p4"
#include "include/packet_io.p4"
#include "include/port_counters.p4"
#include "include/table0.p4"
#include "include/mpls.p4"
#include "include/checksums.p4"
#include "include/int_parser.p4"
#include "include/int_source.p4"
#include "include/int_transit.p4"
#include "include/int_sink.p4"
#include "include/int_report.p4"


control ingress (
    inout headers_t hdr,
    inout local_metadata_t local_metadata,
    inout standard_metadata_t standard_metadata) {

    apply {
        if(local_metadata.l4_dst_port == 5353)
        {
            mark_to_drop(standard_metadata);
            exit;
        }

        port_counters_ingress.apply(hdr, standard_metadata);
        packetio_ingress.apply(hdr, standard_metadata);

        if(hdr.mpls_stack[0].isValid()) {
            local_metadata.mpls_evaluate = true;
            local_metadata.function_int = false;
            local_metadata.function_id = 0;
            mpls_control.apply(hdr, local_metadata, standard_metadata, 0);
            mpls_control.apply(hdr, local_metadata, standard_metadata, 1);
            mpls_control.apply(hdr, local_metadata, standard_metadata, 2);
            mpls_control.apply(hdr, local_metadata, standard_metadata, 3);
            mpls_control.apply(hdr, local_metadata, standard_metadata, 4);
            mpls_control.apply(hdr, local_metadata, standard_metadata, 5);
            mpls_control.apply(hdr, local_metadata, standard_metadata, 6);
            mpls_control.apply(hdr, local_metadata, standard_metadata, 7);
        } else {
            table0_control.apply(hdr, local_metadata, standard_metadata);
        }

        process_int_source_sink.apply(hdr, local_metadata, standard_metadata);

        //If sending to an intermediate function, start INT
        if(local_metadata.function_int == true)
        {
            local_metadata.int_meta.sink = false;
        }

        if (!hdr.int_header.isValid() && local_metadata.int_meta.source == _TRUE && local_metadata.int_meta.sink != _TRUE && standard_metadata.egress_spec != CPU_PORT) {
            process_int_source.apply(hdr, local_metadata, standard_metadata);
        }

        if (local_metadata.int_meta.sink == _TRUE && hdr.int_header.isValid()) {
            // clone packet for Telemetry Report
            // FIXME: this works only on BMv2
            #ifdef TARGET_BMV2
            clone3(CloneType.I2E, REPORT_MIRROR_SESSION_ID, standard_metadata);
            #endif // TARGET_BMV2
        }
    }
}

control egress (
    inout headers_t hdr,
    inout local_metadata_t local_metadata,
    inout standard_metadata_t standard_metadata) {

    apply {
        if(IS_I2E_CLONE(standard_metadata) && hdr.mpls_stack[0].isValid()) {
            local_metadata.mpls_evaluate = true;
            local_metadata.function_int = false;
            local_metadata.function_id = 0;
            mpls_control.apply(hdr, local_metadata, standard_metadata, 0);
            mpls_control.apply(hdr, local_metadata, standard_metadata, 1);
            mpls_control.apply(hdr, local_metadata, standard_metadata, 2);
            mpls_control.apply(hdr, local_metadata, standard_metadata, 3);
            mpls_control.apply(hdr, local_metadata, standard_metadata, 4);
            mpls_control.apply(hdr, local_metadata, standard_metadata, 5);
            mpls_control.apply(hdr, local_metadata, standard_metadata, 6);
            mpls_control.apply(hdr, local_metadata, standard_metadata, 7);
        }

        if(hdr.int_header.isValid()) {            
            
            process_int_transit.apply(hdr, local_metadata, standard_metadata);
            
            if(local_metadata.function_id != 0)
            {
                hdr.int_switch_id.switch_id = hdr.int_switch_id.switch_id | ((bit<32>) local_metadata.function_id) << 14;      
            }

            #ifdef TARGET_BMV2
            if (IS_I2E_CLONE(standard_metadata)) {
                /* send int report */
                process_int_report.apply(hdr, local_metadata, standard_metadata);
            }

            if (local_metadata.int_meta.sink == _TRUE && !IS_I2E_CLONE(standard_metadata)) {
            #else
            if (local_metadata.int_meta.sink == _TRUE) {
            #endif // TARGET_BMV2
                process_int_sink.apply(hdr, local_metadata, standard_metadata);
            }
        }

        port_counters_egress.apply(hdr, standard_metadata);
        packetio_egress.apply(hdr, standard_metadata);

        //For UDP checksum computation
        local_metadata.l4_len = hdr.ipv4.len - ((bit<16>)hdr.ipv4.ihl) * 4;
    }
}

V1Switch(
    int_parser(),
    verify_checksum_control(),
    ingress(),
    egress(),
    compute_checksum_control(),
    int_deparser()
) main;
