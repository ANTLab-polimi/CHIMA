#define KBUILD_MODNAME "bpf_encapsulator"
#include <linux/ip.h>
#include <linux/if_ether.h>
#include <linux/if_arp.h>

#include "encapsulator/mpls.h"

#define CURSOR_ADVANCE(_target, _cursor, _len,_data_end) \
    ({  _target = _cursor; _cursor += _len; \
        if(unlikely(_cursor > _data_end)) return 1; })

#define CURSOR_ADVANCE_NO_PARSE(_cursor, _len, _data_end) \
    ({  _cursor += _len; \
        if(unlikely(_cursor > _data_end)) return 1; })

#define MAPS_SIZE _MAPS_SIZE /*This value comes from build flags*/

#define PACKET_HOST 0
#define BPF_ADJ_ROOM_MAC 1

struct mac_addr{
    uint8_t value[ETH_ALEN];
} __attribute__((packed));

//IP source and destination to identify the rule
struct ips_key{
    uint32_t src;
    uint32_t dst;
} __attribute__((packed));

//Hashmap of destination to label stack mappings
BPF_HASH(dst_stacks_map, struct ips_key, struct mpls_stack, MAPS_SIZE);

//Adapted from
//https://github.com/fzakaria/ebpf-mpls-encap-decap/blob/master/mpls_bpf_kern.c#L217
int encapsulator(struct __sk_buff *skb) {
    void* data_end = (void *)(long)skb->data_end;
    void* cursor = (void *)(long)skb->data;

    //IP addresses used for later checks in the map
    struct ips_key ips;    

    //Read eth header
    struct ethhdr *eth;
    CURSOR_ADVANCE(eth, cursor, sizeof(struct ethhdr), data_end);

    struct iphdr *ip;
    //Understand if we are interested in the next header
    if(ntohs(eth->h_proto) == ETH_P_IP)
    {
        //Read ip header
        CURSOR_ADVANCE(ip, cursor, sizeof(struct iphdr), data_end);

        ips.src = ip->saddr;
        ips.dst = ip->daddr;
    }
    else
        return 1;

    //Declare label stack pointer
    struct mpls_stack *mpls;

    //Check if the destination is in the map
    mpls = dst_stacks_map.lookup(&ips);
    if(mpls == NULL)
    {
        //Not one of our destination, let the packet go
        return 1;
    }

    //Change ethernet proto to MPLS
    eth->h_proto = htons(ETH_P_MPLS_UC);

    uint32_t decoded_label;
    for(uint8_t i=0; i<MAX_MPLS_STACK_SIZE && i<mpls->size; i++)
    {
        decoded_label = ntohl(mpls->stack[i].value);
        if ( (decoded_label & 0xc0000000) == 0xc0000000 && (decoded_label & 0x3ffff000) != 0 )
        {
            ip->tos = 0x17<<2;
        }
    }

    size_t stack_size = 0;
    if(mpls->size > MAX_MPLS_STACK_SIZE)
        stack_size = sizeof(struct mpls_hdr) * MAX_MPLS_STACK_SIZE;
    else
        stack_size = sizeof(struct mpls_hdr) * mpls->size;

    //Add space between eth and ipv4 headers for the label stack
	if ( bpf_skb_adjust_room(skb, (int)stack_size, BPF_ADJ_ROOM_MAC, 0) )
    {
        bpf_trace_printk("Error adjusting room\n");
        return -1;
    }

    //Offset to write just after the eth header
    unsigned long offset = sizeof(struct ethhdr);

    //Write the values in the packet, except for the bos
    for(uint8_t i=0; i<MAX_MPLS_STACK_SIZE && i<mpls->size; i++)
    {
        bpf_skb_store_bytes(skb, (int)offset, &(mpls->stack[i]), sizeof(struct mpls_hdr), BPF_F_RECOMPUTE_CSUM);
        offset += sizeof(struct mpls_hdr);
    }

    return 1;
}
