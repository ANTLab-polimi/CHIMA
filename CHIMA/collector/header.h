#define HASHMAP_LINK_SIZE _HASHMAP_LINK_SIZE
#define HASHMAP_FED_LINK_SIZE _HASHMAP_FED_LINK_SIZE
#define INT_DST_PORT _INT_DST_PORT
#define MAX_INT_HOP _MAX_INT_HOP
#define SHR_EWMA _SHR_EWMA

#define CURSOR_ADVANCE(_target, _cursor, _len,_data_end) \
    ({  _target = _cursor; _cursor += _len; \
        if(unlikely(_cursor > _data_end)) return XDP_DROP; })

#define CURSOR_ADVANCE_NO_PARSE(_cursor, _len, _data_end) \
    ({  _cursor += _len; \
        if(unlikely(_cursor > _data_end)) return XDP_DROP; })

/* INT 1.0 structures from
https://github.com/p4lang/p4-applications/raw/master/docs/INT_v1_0.pdf
https://github.com/p4lang/p4-applications/raw/master/docs/telemetry_report_v1_0.pdf
*/

struct INT_telemetry_report_t {
#if defined(__BIG_ENDIAN_BITFIELD)
    uint8_t  ver:4, len:4;
    uint16_t nProto:3, repMdBits:6, reserved:6, d:1;
    uint8_t  q:1, f:1, hw_id:6;
#elif defined(__LITTLE_ENDIAN_BITFIELD)
    uint8_t  len:4, ver:4;
    uint16_t d:1, reserved:6, repMdBits:6, nProto:3;
    uint8_t  hw_id:6, f:1, q:1;
#else
#error  "Please fix <asm/byteorder.h>"
#endif
    uint32_t sw_id;
    uint32_t seqNumber;
    uint32_t ingressTimestamp;
} __attribute__((packed));

struct INT_shim_t {
    uint8_t type;
    uint8_t shimRsvd;
    uint8_t length;
#if defined(__BIG_ENDIAN_BITFIELD)
    uint8_t  DSCP:6, r:2;
#elif defined(__LITTLE_ENDIAN_BITFIELD)
    uint8_t  r:2, DSCP:6;
#else
#error  "Please fix <asm/byteorder.h>"
#endif
} __attribute__((packed));

struct INT_metadata_fixed_t {
#if defined(__BIG_ENDIAN_BITFIELD)
    uint8_t  ver:4, rep:2, c:1, e:1;
    uint8_t  m:1, rsvd_1a:7;
    uint8_t  rsvd_1b:3, hopMlen:5;
#elif defined(__LITTLE_ENDIAN_BITFIELD)
    uint8_t  e:1, c:1, rep:2, ver:4;
    uint8_t  rsvd_1a:7, m:1;
    uint8_t  hopMlen:5, rsvd_1b:3;
#else
#error  "Please fix <asm/byteorder.h>"
#endif
    uint8_t  rmnHopCnt;
    uint16_t ins;
    uint16_t rsvd_2;
} __attribute__((packed));

struct INT_metadata_stack_t {
  uint32_t sw_id;
  uint32_t ingressTimestamp;
  uint32_t egressTimestamp;
} __attribute__((packed));

struct link_key_t {
  uint32_t switch_id_1;
  uint32_t switch_id_2;
};

struct link_fed_key_t {
    struct link_key_t link_key;
    uint32_t vlan_id;
};

struct link_metrics_t {
  uint32_t latency;
  int32_t jitter;
  uint32_t alignment_padding;
};