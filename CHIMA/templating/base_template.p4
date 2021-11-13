error {
    unknownFunction
}
#include <core.p4>
#define V1MODEL_VERSION 20180101
#include <v1model.p4>

typedef bit<48> mac_t;
typedef bit<32> ip_address_t;
typedef bit<16> l4_port_t;
typedef bit<9> port_t;
typedef bit<16> next_hop_id_t;
const port_t CPU_PORT = 255;
typedef bit<8> MeterColor;
const MeterColor MeterColor_GREEN = 8w0;
const MeterColor MeterColor_YELLOW = 8w1;
const MeterColor MeterColor_RED = 8w2;
@controller_header("packet_in") header packet_in_header_t {
    bit<9> ingress_port;
    bit<7> _padding;
}

@controller_header("packet_out") header packet_out_header_t {
    bit<9> egress_port;
    bit<7> _padding;
}

header ethernet_t {
    bit<48> dst_addr;
    bit<48> src_addr;
    bit<16> ether_type;
}

const bit<8> ETH_HEADER_LEN = 14;
header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<6>  dscp;
    bit<2>  ecn;
    bit<16> len;
    bit<16> identification;
    bit<3>  flags;
    bit<13> frag_offset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdr_checksum;
    bit<32> src_addr;
    bit<32> dst_addr;
}

const bit<8> IPV4_MIN_HEAD_LEN = 20;
header mpls_t {
    bit<2>  type;
    bit<18> label;
    bit<3>  tc;
    bit<1>  bos;
    bit<8>  ttl;
}

header tcp_t {
    bit<16> src_port;
    bit<16> dst_port;
    bit<32> seq_no;
    bit<32> ack_no;
    bit<4>  data_offset;
    bit<3>  res;
    bit<3>  ecn;
    bit<6>  ctrl;
    bit<16> window;
    bit<16> checksum;
    bit<16> urgent_ptr;
}

header tcp_options_t {
    varbit<320> options;
}

header udp_t {
    bit<16> src_port;
    bit<16> dst_port;
    bit<16> length_;
    bit<16> checksum;
}

const bit<8> UDP_HEADER_LEN = 8;
action nop() {
    NoAction();
}
const bit<16> MTU = 1500;
const bit<6> DSCP_INT = 0x17;
const bit<6> DSCP_MASK = 0x3f;
typedef bit<48> timestamp_t;
typedef bit<32> switch_id_t;
const bit<8> INT_HEADER_LEN_WORD = 3;
const bit<16> INT_HEADER_SIZE = 8;
const bit<16> INT_SHIM_HEADER_SIZE = 4;
const bit<16> MAX_INT_TRANSIT_HEADERS_SIZE = 4 * 8;
const bit<8> CPU_MIRROR_SESSION_ID = 250;
const bit<32> REPORT_MIRROR_SESSION_ID = 500;
const bit<6> HW_ID = 1;
const bit<8> REPORT_HDR_TTL = 64;
const bit<32> BMV2_V1MODEL_INSTANCE_TYPE_NORMAL = 0;
const bit<32> BMV2_V1MODEL_INSTANCE_TYPE_INGRESS_CLONE = 1;
const bit<32> BMV2_V1MODEL_INSTANCE_TYPE_EGRESS_CLONE = 2;
const bit<32> BMV2_V1MODEL_INSTANCE_TYPE_COALESCED = 3;
const bit<32> BMV2_V1MODEL_INSTANCE_TYPE_RECIRC = 4;
const bit<32> BMV2_V1MODEL_INSTANCE_TYPE_REPLICATION = 5;
const bit<32> BMV2_V1MODEL_INSTANCE_TYPE_RESUBMIT = 6;
const bit<3> NPROTO_ETHERNET = 0;
const bit<3> NPROTO_TELEMETRY_DROP_HEADER = 1;
const bit<3> NPROTO_TELEMETRY_SWITCH_LOCAL_HEADER = 2;
header report_fixed_header_t {
    bit<4>  ver;
    bit<4>  len;
    bit<3>  nproto;
    bit<6>  rep_md_bits;
    bit<1>  d;
    bit<1>  q;
    bit<1>  f;
    bit<6>  rsvd;
    bit<6>  hw_id;
    bit<32> sw_id;
    bit<32> seq_no;
    bit<32> ingress_tstamp;
}

const bit<8> REPORT_FIXED_HEADER_LEN = 16;
header drop_report_header_t {
    bit<32> switch_id;
    bit<16> ingress_port_id;
    bit<16> egress_port_id;
    bit<8>  queue_id;
    bit<8>  drop_reason;
    bit<16> pad;
}

const bit<8> DROP_REPORT_HEADER_LEN = 12;
header local_report_header_t {
    bit<32> switch_id;
    bit<16> ingress_port_id;
    bit<16> egress_port_id;
    bit<8>  queue_id;
    bit<24> queue_occupancy;
    bit<32> egress_tstamp;
}

const bit<8> LOCAL_REPORT_HEADER_LEN = 16;
header_union local_report_t {
    drop_report_header_t  drop_report_header;
    local_report_header_t local_report_header;
}

header int_header_t {
    bit<4>  ver;
    bit<2>  rep;
    bit<1>  c;
    bit<1>  e;
    bit<1>  m;
    bit<7>  rsvd1;
    bit<3>  rsvd2;
    bit<5>  hop_metadata_len;
    bit<8>  remaining_hop_cnt;
    bit<4>  instruction_mask_0003;
    bit<4>  instruction_mask_0407;
    bit<4>  instruction_mask_0811;
    bit<4>  instruction_mask_1215;
    bit<16> rsvd3;
}

header int_switch_id_t {
    bit<32> switch_id;
}

header int_level1_port_ids_t {
    bit<16> ingress_port_id;
    bit<16> egress_port_id;
}

header int_hop_latency_t {
    bit<32> hop_latency;
}

header int_q_occupancy_t {
    bit<8>  q_id;
    bit<24> q_occupancy;
}

header int_ingress_tstamp_t {
    bit<32> ingress_tstamp;
}

header int_egress_tstamp_t {
    bit<32> egress_tstamp;
}

header int_level2_port_ids_t {
    bit<32> ingress_port_id;
    bit<32> egress_port_id;
}

header int_egress_port_tx_util_t {
    bit<32> egress_port_tx_util;
}

header int_data_t {
    varbit<1920> data;
}

header intl4_shim_t {
    bit<8> int_type;
    bit<8> rsvd1;
    bit<8> len;
    bit<6> dscp;
    bit<2> rsvd2;
}

const bit<16> TSTAMP_HEADER_LEN = 8;
struct int_metadata_t {
    switch_id_t switch_id;
    bit<16>     new_bytes;
    bit<8>      new_words;
    bool        source;
    bool        sink;
    bool        transit;
    bit<8>      intl4_shim_len;
}

struct headers_t {
    packet_out_header_t       packet_out;
    packet_in_header_t        packet_in;
    ethernet_t                report_ethernet;
    ipv4_t                    report_ipv4;
    udp_t                     report_udp;
    report_fixed_header_t     report_fixed_header;
    local_report_t            report_local;
    ethernet_t                ethernet;
    ipv4_t                    ipv4;
    tcp_t                     tcp;
    tcp_options_t             tcp_options;
    udp_t                     udp;
    mpls_t[8]                 mpls_stack;
    intl4_shim_t              intl4_shim;
    int_header_t              int_header;
    int_data_t                int_data;
    int_switch_id_t           int_switch_id;
    int_level1_port_ids_t     int_level1_port_ids;
    int_hop_latency_t         int_hop_latency;
    int_q_occupancy_t         int_q_occupancy;
    int_ingress_tstamp_t      int_ingress_tstamp;
    int_egress_tstamp_t       int_egress_tstamp;
    int_level2_port_ids_t     int_level2_port_ids;
    int_egress_port_tx_util_t int_egress_tx_util;
}

struct local_metadata_t {
    bit<16>        l4_src_port;
    bit<16>        l4_dst_port;
    bit<16>        l4_len;
    next_hop_id_t  next_hop_id;
    bit<16>        selector;
    int_metadata_t int_meta;
    bool           compute_checksum;
    bool           mpls_evaluate;
    bool           function_int;
    bit<18>        function_id;
}

control packetio_ingress(inout headers_t hdr, inout standard_metadata_t standard_metadata) {
    apply {
        if (standard_metadata.ingress_port == CPU_PORT) {
            standard_metadata.egress_spec = hdr.packet_out.egress_port;
            hdr.packet_out.setInvalid();
            exit;
        }
    }
}

control packetio_egress(inout headers_t hdr, inout standard_metadata_t standard_metadata) {
    apply {
        if (standard_metadata.egress_port == CPU_PORT) {
            hdr.packet_in.setValid();
            hdr.packet_in.ingress_port = standard_metadata.ingress_port;
        }
    }
}

control port_counters_ingress(inout headers_t hdr, inout standard_metadata_t standard_metadata) {
    counter(511, CounterType.packets) ingress_port_counter;
    apply {
        ingress_port_counter.count((bit<32>)standard_metadata.ingress_port);
    }
}

control port_counters_egress(inout headers_t hdr, inout standard_metadata_t standard_metadata) {
    counter(511, CounterType.packets) egress_port_counter;
    apply {
        egress_port_counter.count((bit<32>)standard_metadata.egress_port);
    }
}

control table0_control(inout headers_t hdr, inout local_metadata_t local_metadata, inout standard_metadata_t standard_metadata) {
    direct_counter(CounterType.packets_and_bytes) table0_counter;
    action set_next_hop_id(next_hop_id_t next_hop_id) {
        local_metadata.next_hop_id = next_hop_id;
    }
    action send_to_cpu() {
        standard_metadata.egress_spec = CPU_PORT;
    }
    action set_egress_port(port_t port) {
        standard_metadata.egress_spec = port;
    }
    action drop() {
        mark_to_drop(standard_metadata);
    }
    table table0 {
        key = {
            standard_metadata.ingress_port: ternary;
            hdr.ethernet.src_addr         : ternary;
            hdr.ethernet.dst_addr         : ternary;
            hdr.ethernet.ether_type       : ternary;
            hdr.ipv4.src_addr             : ternary;
            hdr.ipv4.dst_addr             : ternary;
            hdr.ipv4.protocol             : ternary;
            local_metadata.l4_src_port    : ternary;
            local_metadata.l4_dst_port    : ternary;
        }
        actions = {
            set_egress_port;
            send_to_cpu;
            set_next_hop_id;
            drop;
        }
        const default_action = drop();
        counters = table0_counter;
    }
    apply {
        table0.apply();
    }
}

###FUNCTION_INCLUDE###
control mpls_control(inout headers_t hdr, inout local_metadata_t local_metadata, inout standard_metadata_t standard_metadata, bit<3> index) {
	###FUNCTION_DEFINE###
    apply {
        if (local_metadata.mpls_evaluate) {
            if (hdr.mpls_stack[index].type == 2) {
                standard_metadata.egress_spec = (port_t)hdr.mpls_stack[index].label;
                local_metadata.mpls_evaluate = false;
            } else if (hdr.mpls_stack[index].type == 3) {
                if (hdr.mpls_stack[index].label == 0) {
                    local_metadata.function_int = true;
                } else {
                    local_metadata.function_id = hdr.mpls_stack[index].label;
                }
            } else if (hdr.mpls_stack[index].type == 1) {
					###FUNCTION_APPLY###
            }
            hdr.mpls_stack[index].setInvalid();
            if (hdr.mpls_stack[index].bos == 1) {
                hdr.ethernet.ether_type = 0x800;
            }
        }
    }
}

control verify_checksum_control(inout headers_t hdr, inout local_metadata_t local_metadata) {
    apply {
    }
}

control compute_checksum_control(inout headers_t hdr, inout local_metadata_t local_metadata) {
    apply {
        update_checksum(hdr.ipv4.isValid(), { hdr.ipv4.version, hdr.ipv4.ihl, hdr.ipv4.dscp, hdr.ipv4.ecn, hdr.ipv4.len, hdr.ipv4.identification, hdr.ipv4.flags, hdr.ipv4.frag_offset, hdr.ipv4.ttl, hdr.ipv4.protocol, hdr.ipv4.src_addr, hdr.ipv4.dst_addr }, hdr.ipv4.hdr_checksum, HashAlgorithm.csum16);
        update_checksum_with_payload(local_metadata.function_int, { hdr.ipv4.src_addr, hdr.ipv4.dst_addr, 8w0, hdr.ipv4.protocol, local_metadata.l4_len, hdr.udp.src_port, hdr.udp.dst_port, hdr.udp.length_, hdr.intl4_shim, hdr.int_header, hdr.int_switch_id, hdr.int_ingress_tstamp, hdr.int_egress_tstamp, hdr.int_data }, hdr.udp.checksum, HashAlgorithm.csum16);
        update_checksum_with_payload(!local_metadata.function_int, { hdr.ipv4.src_addr, hdr.ipv4.dst_addr, 8w0, hdr.ipv4.protocol, local_metadata.l4_len, hdr.udp.src_port, hdr.udp.dst_port, hdr.udp.length_ }, hdr.udp.checksum, HashAlgorithm.csum16);
        update_checksum(hdr.report_ipv4.isValid(), { hdr.report_ipv4.version, hdr.report_ipv4.ihl, hdr.report_ipv4.dscp, hdr.report_ipv4.ecn, hdr.report_ipv4.len, hdr.report_ipv4.identification, hdr.report_ipv4.flags, hdr.report_ipv4.frag_offset, hdr.report_ipv4.ttl, hdr.report_ipv4.protocol, hdr.report_ipv4.src_addr, hdr.report_ipv4.dst_addr }, hdr.report_ipv4.hdr_checksum, HashAlgorithm.csum16);
    }
}

parser int_parser(packet_in packet, out headers_t hdr, inout local_metadata_t local_metadata, inout standard_metadata_t standard_metadata) {
    state start {
        transition select(standard_metadata.ingress_port) {
            CPU_PORT: parse_packet_out;
            default: parse_ethernet;
        }
    }
    state parse_packet_out {
        packet.extract(hdr.packet_out);
        transition parse_ethernet;
    }
    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.ether_type) {
            0x800: parse_ipv4;
            0x8847: parse_mpls;
            default: accept;
        }
    }
    state parse_mpls {
        packet.extract(hdr.mpls_stack.next);
        transition select(hdr.mpls_stack.last.bos) {
            0: parse_mpls;
            1: parse_ipv4;
        }
    }
    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            8w6: parse_tcp;
            8w17: parse_udp;
            default: accept;
        }
    }
    state parse_tcp {
        packet.extract(hdr.tcp);
        local_metadata.l4_src_port = hdr.tcp.src_port;
        local_metadata.l4_dst_port = hdr.tcp.dst_port;
        transition select(hdr.tcp.data_offset - 4w5) {
            4w0: detect_intl4_shim;
            default: parse_tcp_options;
        }
    }
    state parse_tcp_options {
        packet.extract(hdr.tcp_options, (bit<32>)hdr.tcp.data_offset - 32w5 << 5);
        transition detect_intl4_shim;
    }
    state parse_udp {
        packet.extract(hdr.udp);
        local_metadata.l4_src_port = hdr.udp.src_port;
        local_metadata.l4_dst_port = hdr.udp.dst_port;
        transition detect_intl4_shim;
    }
    state detect_intl4_shim {
        transition select(hdr.ipv4.dscp) {
            DSCP_INT &&& DSCP_MASK: parse_intl4_shim;
            default: accept;
        }
    }
    state parse_intl4_shim {
        packet.extract(hdr.intl4_shim);
        local_metadata.int_meta.intl4_shim_len = hdr.intl4_shim.len;
        transition parse_int_header;
    }
    state parse_int_header {
        packet.extract(hdr.int_header);
        transition parse_int_data;
    }
    state parse_int_data {
        packet.extract(hdr.int_data, (bit<32>)(local_metadata.int_meta.intl4_shim_len - INT_HEADER_LEN_WORD) << 5);
        transition accept;
    }
}

control int_deparser(packet_out packet, in headers_t hdr) {
    apply {
        packet.emit(hdr.packet_in);
        packet.emit(hdr.report_ethernet);
        packet.emit(hdr.report_ipv4);
        packet.emit(hdr.report_udp);
        packet.emit(hdr.report_fixed_header);
        packet.emit(hdr.ethernet);
        packet.emit(hdr.mpls_stack);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.tcp);
        packet.emit(hdr.tcp_options);
        packet.emit(hdr.udp);
        packet.emit(hdr.intl4_shim);
        packet.emit(hdr.int_header);
        packet.emit(hdr.int_switch_id);
        packet.emit(hdr.int_level1_port_ids);
        packet.emit(hdr.int_hop_latency);
        packet.emit(hdr.int_q_occupancy);
        packet.emit(hdr.int_ingress_tstamp);
        packet.emit(hdr.int_egress_tstamp);
        packet.emit(hdr.int_level2_port_ids);
        packet.emit(hdr.int_egress_tx_util);
        packet.emit(hdr.int_data);
    }
}

control process_int_source(inout headers_t hdr, inout local_metadata_t local_metadata, inout standard_metadata_t standard_metadata) {
    direct_counter(CounterType.packets_and_bytes) counter_int_source;
    action int_source(bit<5> hop_metadata_len, bit<8> remaining_hop_cnt, bit<4> ins_mask0003, bit<4> ins_mask0407) {
        hdr.intl4_shim.setValid();
        hdr.intl4_shim.int_type = 1;
        hdr.intl4_shim.len = INT_HEADER_LEN_WORD;
        hdr.intl4_shim.dscp = hdr.ipv4.dscp;
        hdr.int_header.setValid();
        hdr.int_header.ver = 0;
        hdr.int_header.rep = 0;
        hdr.int_header.c = 0;
        hdr.int_header.e = 0;
        hdr.int_header.m = 0;
        hdr.int_header.rsvd1 = 0;
        hdr.int_header.rsvd2 = 0;
        hdr.int_header.hop_metadata_len = hop_metadata_len;
        hdr.int_header.remaining_hop_cnt = remaining_hop_cnt;
        hdr.int_header.instruction_mask_0003 = ins_mask0003;
        hdr.int_header.instruction_mask_0407 = ins_mask0407;
        hdr.int_header.instruction_mask_0811 = 0;
        hdr.int_header.instruction_mask_1215 = 0;
        hdr.ipv4.len = hdr.ipv4.len + INT_HEADER_SIZE + INT_SHIM_HEADER_SIZE;
        hdr.udp.length_ = hdr.udp.length_ + INT_HEADER_SIZE + INT_SHIM_HEADER_SIZE;
    }
    action int_source_dscp(bit<5> hop_metadata_len, bit<8> remaining_hop_cnt, bit<4> ins_mask0003, bit<4> ins_mask0407) {
        int_source(hop_metadata_len, remaining_hop_cnt, ins_mask0003, ins_mask0407);
        hdr.ipv4.dscp = DSCP_INT;
        counter_int_source.count();
    }
    table tb_int_source {
        key = {
            hdr.ipv4.src_addr         : ternary;
            hdr.ipv4.dst_addr         : ternary;
            hdr.ipv4.protocol         : ternary;
            local_metadata.l4_src_port: ternary;
            local_metadata.l4_dst_port: ternary;
        }
        actions = {
            int_source_dscp;
            @defaultonly nop();
        }
        counters = counter_int_source;
        const default_action = nop();
    }
    apply {
        if ((bit<16>)standard_metadata.packet_length + INT_SHIM_HEADER_SIZE + INT_HEADER_SIZE + MAX_INT_TRANSIT_HEADERS_SIZE < MTU) {
            tb_int_source.apply();
        }
    }
}

control process_int_source_sink(inout headers_t hdr, inout local_metadata_t local_metadata, inout standard_metadata_t standard_metadata) {
    direct_counter(CounterType.packets_and_bytes) counter_set_source;
    direct_counter(CounterType.packets_and_bytes) counter_set_sink;
    action int_set_source() {
        local_metadata.int_meta.source = true;
        counter_set_source.count();
    }
    action int_set_sink() {
        local_metadata.int_meta.sink = true;
        counter_set_sink.count();
    }
    table tb_set_source {
        key = {
            standard_metadata.ingress_port: exact;
        }
        actions = {
            int_set_source;
            @defaultonly nop();
        }
        counters = counter_set_source;
        const default_action = nop();
        size = 511;
    }
    table tb_set_sink {
        key = {
            standard_metadata.egress_spec: exact;
        }
        actions = {
            int_set_sink;
            @defaultonly nop();
        }
        counters = counter_set_sink;
        const default_action = nop();
        size = 511;
    }
    apply {
        tb_set_source.apply();
        tb_set_sink.apply();
    }
}

control process_int_transit(inout headers_t hdr, inout local_metadata_t local_metadata, inout standard_metadata_t standard_metadata) {
    action init_metadata(switch_id_t switch_id) {
        local_metadata.int_meta.transit = true;
        local_metadata.int_meta.switch_id = switch_id;
    }
    @hidden action int_set_header_0() {
        hdr.int_switch_id.setValid();
        hdr.int_switch_id.switch_id = local_metadata.int_meta.switch_id;
    }
    @hidden action int_set_header_1() {
        hdr.int_level1_port_ids.setValid();
        hdr.int_level1_port_ids.ingress_port_id = (bit<16>)standard_metadata.ingress_port;
        hdr.int_level1_port_ids.egress_port_id = (bit<16>)standard_metadata.egress_port;
    }
    @hidden action int_set_header_2() {
        hdr.int_hop_latency.setValid();
        hdr.int_hop_latency.hop_latency = (bit<32>)standard_metadata.egress_global_timestamp - (bit<32>)standard_metadata.ingress_global_timestamp;
    }
    @hidden action int_set_header_3() {
        hdr.int_q_occupancy.setValid();
        hdr.int_q_occupancy.q_id = 0;
        hdr.int_q_occupancy.q_occupancy = (bit<24>)standard_metadata.deq_qdepth;
    }
    @hidden action int_set_header_4() {
        hdr.int_ingress_tstamp.setValid();
        hdr.int_ingress_tstamp.ingress_tstamp = (bit<32>)standard_metadata.ingress_global_timestamp;
    }
    @hidden action int_set_header_5() {
        hdr.int_egress_tstamp.setValid();
        hdr.int_egress_tstamp.egress_tstamp = (bit<32>)standard_metadata.egress_global_timestamp;
    }
    @hidden action int_set_header_6() {
        hdr.int_level2_port_ids.setValid();
        hdr.int_level2_port_ids.ingress_port_id = (bit<32>)standard_metadata.ingress_port;
        hdr.int_level2_port_ids.egress_port_id = (bit<32>)standard_metadata.egress_port;
    }
    @hidden action int_set_header_7() {
        hdr.int_egress_tx_util.setValid();
        hdr.int_egress_tx_util.egress_port_tx_util = 0;
    }
    @hidden action add_1() {
        local_metadata.int_meta.new_words = local_metadata.int_meta.new_words + 1;
        local_metadata.int_meta.new_bytes = local_metadata.int_meta.new_bytes + 4;
    }
    @hidden action add_2() {
        local_metadata.int_meta.new_words = local_metadata.int_meta.new_words + 2;
        local_metadata.int_meta.new_bytes = local_metadata.int_meta.new_bytes + 8;
    }
    @hidden action add_3() {
        local_metadata.int_meta.new_words = local_metadata.int_meta.new_words + 3;
        local_metadata.int_meta.new_bytes = local_metadata.int_meta.new_bytes + 12;
    }
    @hidden action add_4() {
        local_metadata.int_meta.new_words = local_metadata.int_meta.new_words + 4;
        local_metadata.int_meta.new_bytes = local_metadata.int_meta.new_bytes + 16;
    }
    @hidden action add_5() {
        local_metadata.int_meta.new_words = local_metadata.int_meta.new_words + 5;
        local_metadata.int_meta.new_bytes = local_metadata.int_meta.new_bytes + 20;
    }
    @hidden action int_set_header_0003_i0() {
    }
    @hidden action int_set_header_0003_i1() {
        int_set_header_3();
        add_1();
    }
    @hidden action int_set_header_0003_i2() {
        int_set_header_2();
        add_1();
    }
    @hidden action int_set_header_0003_i3() {
        int_set_header_3();
        int_set_header_2();
        add_2();
    }
    @hidden action int_set_header_0003_i4() {
        int_set_header_1();
        add_1();
    }
    @hidden action int_set_header_0003_i5() {
        int_set_header_3();
        int_set_header_1();
        add_2();
    }
    @hidden action int_set_header_0003_i6() {
        int_set_header_2();
        int_set_header_1();
        add_2();
    }
    @hidden action int_set_header_0003_i7() {
        int_set_header_3();
        int_set_header_2();
        int_set_header_1();
        add_3();
    }
    @hidden action int_set_header_0003_i8() {
        int_set_header_0();
        add_1();
    }
    @hidden action int_set_header_0003_i9() {
        int_set_header_3();
        int_set_header_0();
        add_2();
    }
    @hidden action int_set_header_0003_i10() {
        int_set_header_2();
        int_set_header_0();
        add_2();
    }
    @hidden action int_set_header_0003_i11() {
        int_set_header_3();
        int_set_header_2();
        int_set_header_0();
        add_3();
    }
    @hidden action int_set_header_0003_i12() {
        int_set_header_1();
        int_set_header_0();
        add_2();
    }
    @hidden action int_set_header_0003_i13() {
        int_set_header_3();
        int_set_header_1();
        int_set_header_0();
        add_3();
    }
    @hidden action int_set_header_0003_i14() {
        int_set_header_2();
        int_set_header_1();
        int_set_header_0();
        add_3();
    }
    @hidden action int_set_header_0003_i15() {
        int_set_header_3();
        int_set_header_2();
        int_set_header_1();
        int_set_header_0();
        add_4();
    }
    @hidden action int_set_header_0407_i0() {
    }
    @hidden action int_set_header_0407_i1() {
        int_set_header_7();
        add_1();
    }
    @hidden action int_set_header_0407_i2() {
        int_set_header_6();
        add_2();
    }
    @hidden action int_set_header_0407_i3() {
        int_set_header_7();
        int_set_header_6();
        add_3();
    }
    @hidden action int_set_header_0407_i4() {
        int_set_header_5();
        add_1();
    }
    @hidden action int_set_header_0407_i5() {
        int_set_header_7();
        int_set_header_5();
        add_2();
    }
    @hidden action int_set_header_0407_i6() {
        int_set_header_6();
        int_set_header_5();
        add_3();
    }
    @hidden action int_set_header_0407_i7() {
        int_set_header_7();
        int_set_header_6();
        int_set_header_5();
        add_4();
    }
    @hidden action int_set_header_0407_i8() {
        int_set_header_4();
        add_1();
    }
    @hidden action int_set_header_0407_i9() {
        int_set_header_7();
        int_set_header_4();
        add_2();
    }
    @hidden action int_set_header_0407_i10() {
        int_set_header_6();
        int_set_header_4();
        add_3();
    }
    @hidden action int_set_header_0407_i11() {
        int_set_header_7();
        int_set_header_6();
        int_set_header_4();
        add_4();
    }
    @hidden action int_set_header_0407_i12() {
        int_set_header_5();
        int_set_header_4();
        add_2();
    }
    @hidden action int_set_header_0407_i13() {
        int_set_header_7();
        int_set_header_5();
        int_set_header_4();
        add_3();
    }
    @hidden action int_set_header_0407_i14() {
        int_set_header_6();
        int_set_header_5();
        int_set_header_4();
        add_4();
    }
    @hidden action int_set_header_0407_i15() {
        int_set_header_7();
        int_set_header_6();
        int_set_header_5();
        int_set_header_4();
        add_5();
    }
    table tb_int_insert {
        key = {
            hdr.int_header.isValid(): exact @name("int_is_valid") ;
        }
        actions = {
            init_metadata;
            @defaultonly nop;
        }
        const default_action = nop();
        size = 1;
    }
    @hidden table tb_int_inst_0003 {
        key = {
            hdr.int_header.instruction_mask_0003: exact;
        }
        actions = {
            int_set_header_0003_i0;
            int_set_header_0003_i1;
            int_set_header_0003_i2;
            int_set_header_0003_i3;
            int_set_header_0003_i4;
            int_set_header_0003_i5;
            int_set_header_0003_i6;
            int_set_header_0003_i7;
            int_set_header_0003_i8;
            int_set_header_0003_i9;
            int_set_header_0003_i10;
            int_set_header_0003_i11;
            int_set_header_0003_i12;
            int_set_header_0003_i13;
            int_set_header_0003_i14;
            int_set_header_0003_i15;
        }
        const entries = {
                        0x0 : int_set_header_0003_i0();
                        0x1 : int_set_header_0003_i1();
                        0x2 : int_set_header_0003_i2();
                        0x3 : int_set_header_0003_i3();
                        0x4 : int_set_header_0003_i4();
                        0x5 : int_set_header_0003_i5();
                        0x6 : int_set_header_0003_i6();
                        0x7 : int_set_header_0003_i7();
                        0x8 : int_set_header_0003_i8();
                        0x9 : int_set_header_0003_i9();
                        0xa : int_set_header_0003_i10();
                        0xb : int_set_header_0003_i11();
                        0xc : int_set_header_0003_i12();
                        0xd : int_set_header_0003_i13();
                        0xe : int_set_header_0003_i14();
                        0xf : int_set_header_0003_i15();
        }
    }
    @hidden table tb_int_inst_0407 {
        key = {
            hdr.int_header.instruction_mask_0407: exact;
        }
        actions = {
            int_set_header_0407_i0;
            int_set_header_0407_i1;
            int_set_header_0407_i2;
            int_set_header_0407_i3;
            int_set_header_0407_i4;
            int_set_header_0407_i5;
            int_set_header_0407_i6;
            int_set_header_0407_i7;
            int_set_header_0407_i8;
            int_set_header_0407_i9;
            int_set_header_0407_i10;
            int_set_header_0407_i11;
            int_set_header_0407_i12;
            int_set_header_0407_i13;
            int_set_header_0407_i14;
            int_set_header_0407_i15;
        }
        const entries = {
                        0x0 : int_set_header_0407_i0();
                        0x1 : int_set_header_0407_i1();
                        0x2 : int_set_header_0407_i2();
                        0x3 : int_set_header_0407_i3();
                        0x4 : int_set_header_0407_i4();
                        0x5 : int_set_header_0407_i5();
                        0x6 : int_set_header_0407_i6();
                        0x7 : int_set_header_0407_i7();
                        0x8 : int_set_header_0407_i8();
                        0x9 : int_set_header_0407_i9();
                        0xa : int_set_header_0407_i10();
                        0xb : int_set_header_0407_i11();
                        0xc : int_set_header_0407_i12();
                        0xd : int_set_header_0407_i13();
                        0xe : int_set_header_0407_i14();
                        0xf : int_set_header_0407_i15();
        }
    }
    apply {
        if ((bit<16>)standard_metadata.packet_length + MAX_INT_TRANSIT_HEADERS_SIZE < MTU) {
            tb_int_insert.apply();
            if (local_metadata.int_meta.transit == false) {
                return;
            }
            tb_int_inst_0003.apply();
            tb_int_inst_0407.apply();
            hdr.int_header.remaining_hop_cnt = hdr.int_header.remaining_hop_cnt - 1;
            if (hdr.ipv4.isValid()) {
                hdr.ipv4.len = hdr.ipv4.len + local_metadata.int_meta.new_bytes;
            }
            if (hdr.udp.isValid()) {
                hdr.udp.length_ = hdr.udp.length_ + local_metadata.int_meta.new_bytes;
            }
            if (hdr.intl4_shim.isValid()) {
                hdr.intl4_shim.len = hdr.intl4_shim.len + local_metadata.int_meta.new_words;
            }
        }
    }
}

control process_int_sink(inout headers_t hdr, inout local_metadata_t local_metadata, inout standard_metadata_t standard_metadata) {
    @hidden action restore_header() {
        hdr.ipv4.dscp = hdr.intl4_shim.dscp;
        bit<16> len_bytes = (bit<16>)hdr.intl4_shim.len << 2;
        hdr.ipv4.len = hdr.ipv4.len - len_bytes;
        hdr.udp.length_ = hdr.udp.length_ - len_bytes;
    }
    @hidden action int_sink() {
        hdr.int_header.setInvalid();
        hdr.int_data.setInvalid();
        hdr.intl4_shim.setInvalid();
        hdr.int_switch_id.setInvalid();
        hdr.int_level1_port_ids.setInvalid();
        hdr.int_hop_latency.setInvalid();
        hdr.int_q_occupancy.setInvalid();
        hdr.int_ingress_tstamp.setInvalid();
        hdr.int_egress_tstamp.setInvalid();
        hdr.int_level2_port_ids.setInvalid();
        hdr.int_egress_tx_util.setInvalid();
    }
    apply {
        restore_header();
        int_sink();
    }
}

control process_int_report(inout headers_t hdr, inout local_metadata_t local_metadata, inout standard_metadata_t standard_metadata) {
    action add_report_fixed_header() {
        hdr.report_fixed_header.setValid();
        hdr.report_fixed_header.ver = 1;
        hdr.report_fixed_header.len = 4;
        hdr.report_fixed_header.nproto = NPROTO_ETHERNET;
        hdr.report_fixed_header.rep_md_bits = 0;
        hdr.report_fixed_header.d = 0;
        hdr.report_fixed_header.q = 0;
        hdr.report_fixed_header.f = 1;
        hdr.report_fixed_header.rsvd = 0;
        hdr.report_fixed_header.hw_id = HW_ID;
        hdr.report_fixed_header.sw_id = local_metadata.int_meta.switch_id;
        hdr.report_fixed_header.seq_no = 0;
        hdr.report_fixed_header.ingress_tstamp = (bit<32>)standard_metadata.enq_timestamp;
    }
    action do_report_encapsulation(mac_t src_mac, mac_t mon_mac, ip_address_t src_ip, ip_address_t mon_ip, l4_port_t mon_port) {
        hdr.report_ethernet.setValid();
        hdr.report_ethernet.dst_addr = mon_mac;
        hdr.report_ethernet.src_addr = src_mac;
        hdr.report_ethernet.ether_type = 0x800;
        hdr.report_ipv4.setValid();
        hdr.report_ipv4.version = 4w4;
        hdr.report_ipv4.ihl = 4w5;
        hdr.report_ipv4.dscp = 6w0;
        hdr.report_ipv4.ecn = 2w0;
        hdr.report_ipv4.len = (bit<16>)IPV4_MIN_HEAD_LEN + (bit<16>)UDP_HEADER_LEN + (bit<16>)REPORT_FIXED_HEADER_LEN + (bit<16>)ETH_HEADER_LEN + hdr.ipv4.len;
        hdr.report_ipv4.identification = 0;
        hdr.report_ipv4.flags = 0;
        hdr.report_ipv4.frag_offset = 0;
        hdr.report_ipv4.ttl = REPORT_HDR_TTL;
        hdr.report_ipv4.protocol = 8w17;
        hdr.report_ipv4.src_addr = src_ip;
        hdr.report_ipv4.dst_addr = mon_ip;
        hdr.report_udp.setValid();
        hdr.report_udp.src_port = 0;
        hdr.report_udp.dst_port = mon_port;
        hdr.report_udp.length_ = (bit<16>)UDP_HEADER_LEN + (bit<16>)REPORT_FIXED_HEADER_LEN + (bit<16>)ETH_HEADER_LEN + hdr.ipv4.len;
        local_metadata.compute_checksum = true;
        add_report_fixed_header();
        truncate((bit<32>)hdr.report_ipv4.len + (bit<32>)ETH_HEADER_LEN);
    }
    table tb_generate_report {
        key = {
            hdr.int_header.isValid(): exact @name("int_is_valid") ;
        }
        actions = {
            do_report_encapsulation;
            @defaultonly nop();
        }
        default_action = nop;
    }
    apply {
        hdr.ethernet.ether_type = 0x800;
        hdr.mpls_stack[0].setInvalid();
        hdr.mpls_stack[1].setInvalid();
        hdr.mpls_stack[2].setInvalid();
        hdr.mpls_stack[3].setInvalid();
        hdr.mpls_stack[4].setInvalid();
        hdr.mpls_stack[5].setInvalid();
        hdr.mpls_stack[6].setInvalid();
        hdr.mpls_stack[7].setInvalid();
        tb_generate_report.apply();
    }
}

control ingress(inout headers_t hdr, inout local_metadata_t local_metadata, inout standard_metadata_t standard_metadata) {
    apply {
        if (local_metadata.l4_dst_port == 5353) {
            mark_to_drop(standard_metadata);
            exit;
        }
        port_counters_ingress.apply(hdr, standard_metadata);
        packetio_ingress.apply(hdr, standard_metadata);
        if (hdr.mpls_stack[0].isValid()) {
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
        if (local_metadata.function_int == true) {
            local_metadata.int_meta.sink = false;
        }
        if (!hdr.int_header.isValid() && local_metadata.int_meta.source == true && local_metadata.int_meta.sink != true && standard_metadata.egress_spec != CPU_PORT) {
            process_int_source.apply(hdr, local_metadata, standard_metadata);
        }
        if (local_metadata.int_meta.sink == true && hdr.int_header.isValid()) {
            clone3(CloneType.I2E, REPORT_MIRROR_SESSION_ID, standard_metadata);
        }
    }
}

control egress(inout headers_t hdr, inout local_metadata_t local_metadata, inout standard_metadata_t standard_metadata) {
    apply {
        if (standard_metadata.instance_type == BMV2_V1MODEL_INSTANCE_TYPE_INGRESS_CLONE && hdr.mpls_stack[0].isValid()) {
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
        if (hdr.int_header.isValid()) {
            process_int_transit.apply(hdr, local_metadata, standard_metadata);
            if (local_metadata.function_id != 0) {
                hdr.int_switch_id.switch_id = hdr.int_switch_id.switch_id | (bit<32>)local_metadata.function_id << 14;
            }
            if (standard_metadata.instance_type == BMV2_V1MODEL_INSTANCE_TYPE_INGRESS_CLONE) {
                process_int_report.apply(hdr, local_metadata, standard_metadata);
            }
            if (local_metadata.int_meta.sink == true && !(standard_metadata.instance_type == BMV2_V1MODEL_INSTANCE_TYPE_INGRESS_CLONE)) {
                process_int_sink.apply(hdr, local_metadata, standard_metadata);
            }
        }
        port_counters_egress.apply(hdr, standard_metadata);
        packetio_egress.apply(hdr, standard_metadata);
        local_metadata.l4_len = hdr.ipv4.len - (bit<16>)hdr.ipv4.ihl * 4;
    }
}

V1Switch(int_parser(), verify_checksum_control(), ingress(), egress(), compute_checksum_control(), int_deparser()) main;

