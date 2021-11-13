all: int constants framework

template:
	python3 apply_templates.py

basic: basic.p4
	@./bmv2-compile.sh "basic" ""

int: int.p4
	@./bmv2-compile.sh "int" "-DTARGET_BMV2"

constants:
	docker run -v $(ONOS_ROOT):/onos -w /onos/tools/dev/bin \
		--entrypoint ./onos-gen-p4-constants opennetworking/p4mn:stable \
		-o /onos/pipelines/basic/src/main/java/org/onosproject/pipelines/basic/BasicConstants.java \
		basic /onos/pipelines/basic/src/main/resources/p4c-out/bmv2/basic_p4info.txt
	docker run -v $(ONOS_ROOT):/onos -w /onos/tools/dev/bin \
		--entrypoint ./onos-gen-p4-constants opennetworking/p4mn:stable \
		-o /onos/pipelines/basic/src/main/java/org/onosproject/pipelines/basic/IntConstants.java \
		int /onos/pipelines/basic/src/main/resources/p4c-out/bmv2/int_p4info.txt

framework:
	./update_framework.sh

clean:
	rm -rf p4c-out/bmv2/*
