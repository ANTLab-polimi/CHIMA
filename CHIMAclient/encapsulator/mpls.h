struct mpls_hdr {
    uint32_t  value;
} __attribute__((packed));

struct mpls_decoded {
    uint32_t label;
    uint8_t tc;
    uint8_t bos;
    uint8_t ttl;
};

#define MAX_MPLS_STACK_SIZE _MAX_MPLS_STACK_SIZE /*This value comes from build flags*/

//Maximum label stack size of 8 labels
struct mpls_stack{
    struct mpls_hdr stack[MAX_MPLS_STACK_SIZE];
    uint8_t size; //How many labels are populated
    //The populated labels start from index 0 to index size-1
} __attribute__((packed));

static __always_inline void mpls_decode(struct mpls_decoded *dec, struct mpls_hdr hdr) {
    uint32_t val = ntohl(hdr.value);
    dec->label = (val & 0xFFFFF000) >> 12;
    dec->tc    = (val & 0x00000E00) >> 9;
    dec->bos   = (val & 0x00000100) >> 8;
    dec->ttl   = val & 0x000000FF;
}

static __always_inline void mpls_encode(struct mpls_hdr *hdr, struct mpls_decoded dec)
{
    uint32_t val = 0;
    val |= ((uint32_t) dec.label & 0xFFFFF) << 12;
    val |= ((uint32_t) dec.tc & 0x7) << 9;
    val |= ((uint32_t) dec.bos & 0x1) << 8;
    val |= (uint32_t) dec.ttl;
    hdr->value = htonl(val);
}