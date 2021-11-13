control changettl_control(
    inout headers_t hdr,
    inout local_metadata_t local_metadata,
    inout standard_metadata_t standard_metadata) {

    apply {
        if(hdr.ipv4.isValid()) {
            hdr.ipv4.ttl = 42;
        }
    }
}
