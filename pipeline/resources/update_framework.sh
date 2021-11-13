#!/bin/bash

cp p4c-out/bmv2/int_pp.p4 $CHIMA_ROOT/CHIMA/templating/base_template.p4
sed -r -i 's/(control mpls_control.+\{)/###FUNCTION_INCLUDE###\n\1\n\t###FUNCTION_DEFINE###/' $CHIMA_ROOT/CHIMA/templating/base_template.p4
sed -r -i 's/(if\s+\(hdr.mpls_stack\[index\]\.type == 1.+\{)/\1\n\t\t\t\t\t###FUNCTION_APPLY###/' $CHIMA_ROOT/CHIMA/templating/base_template.p4