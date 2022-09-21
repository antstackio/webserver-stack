from aws_cdk import Stack
from constructs import Construct
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds
from aws_cdk import SecretValue

class WebserverStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.stack_prefix = 'webserver'
        self.vpc = ec2.Vpc(self,
                           id=f"{self.stack_prefix}-vpc",
                           max_azs=2,
                           cidr='10.0.0.0/16',
                           nat_gateways=0,
                           subnet_configuration=[
                               ec2.SubnetConfiguration(
                                   name=f"{self.stack_prefix}-public-subnet",
                                   subnet_type=ec2.SubnetType.PUBLIC,
                                   cidr_mask=24
                               ),
                               ec2.SubnetConfiguration(
                                   name=f"{self.stack_prefix}-private-subnet",
                                   subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                                   cidr_mask=24)
                           ]
                           )

        self.web_server_sg = ec2.SecurityGroup(self,
                                               id=f"{self.stack_prefix}-web-server-sg",
                                               vpc=self.vpc
                                               )

        self.web_server_sg.add_ingress_rule(peer=ec2.Peer.any_ipv4(), connection=ec2.Port.tcp(
            80), description='Allow HTTP from anywhere')
        self.web_server_sg.add_ingress_rule(peer=ec2.Peer.any_ipv4(), connection=ec2.Port.tcp(
            443), description='Allow HTTPS from anywhere')
        self.web_server_sg.add_ingress_rule(peer=ec2.Peer.any_ipv4(), connection=ec2.Port.tcp(
            22), description='Allow SSH from anywhere')
        self.web_server_sg.add_ingress_rule(peer=ec2.Peer.any_ipv4(), connection=ec2.Port.tcp(
            8080), description='Allow HTTP from anywhere')

        webserver_ec2_instance = ec2.Instance(self,
                                              f"{self.stack_prefix}-webserver-instance",
                                              vpc=self.vpc,
                                              instance_type=ec2.InstanceType.of(
                                                  ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
                                              machine_image=ec2.MachineImage.generic_linux({
                                                  'us-east-1': 'ami-083654bd07b5da81d'}),
                                              key_name="<your ssh key>",
                                              security_group=self.web_server_sg,
                                              vpc_subnets=ec2.SubnetSelection(
                                                  subnet_type=ec2.SubnetType.PUBLIC
                                              ))

        self.db_sg = ec2.SecurityGroup(self,
                                       id=f"{self.stack_prefix}-db-sg",
                                       vpc=self.vpc,
                                       allow_all_outbound=False
                                       )
        self.db_sg.add_ingress_rule(peer=ec2.Peer.security_group_id(self.web_server_sg.security_group_id), connection=ec2.Port.tcp(
            3306), description='Allow port 3306 only to the webserver in order to access the MYSQL')

        db_instance = rds.DatabaseInstance(
            self,
            "rds-instance",
            engine=rds.DatabaseInstanceEngine.MYSQL,
            instance_identifier=f"{self.stack_prefix}-db-instance",
            deletion_protection=False,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO),
            security_groups=[self.db_sg],
            allocated_storage=8,
            credentials=rds.Credentials.from_generated_secret(username='admin'),
            database_name=f"{self.stack_prefix}db",
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
        )
