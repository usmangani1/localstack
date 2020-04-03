from moto.ec2 import models as ec2_models
from moto.ec2.exceptions import InvalidPermissionNotFoundError,MotoNotImplementedError
from localstack import config
from localstack.constants import DEFAULT_PORT_EC2_BACKEND
from localstack.services.infra import start_moto_server


def patch_ec2():
    def patch_revoke_security_group_egress(backend):
        revoke_security_group_egress_orig = backend.revoke_security_group_egress

        def revoke_security_group_egress(*args, **kwargs):
            try:
                return revoke_security_group_egress_orig(*args, **kwargs)
            except InvalidPermissionNotFoundError:
                # this can happen, as CidrIpv6 is not yet supported by moto
                if args[4] == []:
                    return '_ignore_'
        return revoke_security_group_egress

    def patch_describe_instance_credit_specifications(backend):
        describe_instance_credit_specifications_orig = backend.describe_instance_credit_specifications

        def describe_instance_credit_specifications(**kwargs):
            try:
                return describe_instance_credit_specifications_orig(**kwargs)
            except MotoNotImplementedError:
                # this will happen because the moto doesnt support the describe_instance_credit_specifications fucnction.
                if kwargs[0] == []:
                    return '_ignore_'
        return describe_instance_credit_specifications


    for region, backend in ec2_models.ec2_backends.items():
        backend.revoke_security_group_egress = patch_revoke_security_group_egress(backend)
        backend.describe_instance_credit_specifications = patch_describe_instance_credit_specifications(backend)


def start_ec2(port=None, asynchronous=False, update_listener=None):
    patch_ec2()
    port = port or config.PORT_EC2
    return start_moto_server('ec2', port, name='EC2', asynchronous=asynchronous,
        backend_port=DEFAULT_PORT_EC2_BACKEND, update_listener=update_listener)
