.PHONY: ansiblerun, ansiblecheck, servercreate,lstudiorun

ansiblecheck:
	ansible-playbook -i inventory.ini \
	-u ubuntu \
	--key-file ~/.ssh/id_mse_infomaniak_openstack \
	--check \
	server-install.yml

ansiblerun:
	ansible-playbook -i inventory.ini \
	-u ubuntu \
	--key-file ~/.ssh/id_mse_infomaniak_openstack \
	server-install.yml

lstudiorun:
	ansible-playbook -i inventory.ini \
	-u ubuntu \
	--key-file ~/.ssh/id_mse_infomaniak_openstack \
	server-install.yml --tags=lstudio

servercreate:
	./openstack/create_server.sh

