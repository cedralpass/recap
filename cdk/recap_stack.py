from aws_cdk import (aws_ec2 as ec2, 
                     aws_ecs as ecs,
                     aws_ecr as ecr,
                     aws_ecs_patterns as ecs_patterns,
                     Stack, CfnOutput, Duration
                    )
from constructs import Construct
from environs import Env


class RecapAIApiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        env = Env()
        env.read_env()
        container_repo = env("AI_API_Container_Repo")

        # The code that defines your stack goes here
        vpc = ec2.Vpc(self, 
              "RecapAIApiVpc", 
               gateway_endpoints={
                 "S3": ec2.GatewayVpcEndpointOptions(
                    service=ec2.GatewayVpcEndpointAwsService.S3
                  )
               },
               max_azs=2)
        
        # VPC Interface Endpoints
        ec2.InterfaceVpcEndpoint(self, "VPC Endpoint Docker",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointService(f"com.amazonaws.us-west-2.ecr.dkr"),
        )

        ec2.InterfaceVpcEndpoint(self, "VPC Endpoint ECR API",
            vpc=vpc,
            service=ec2.InterfaceVpcEndpointService(f"com.amazonaws.us-west-2.ecr.api"),
        )
        # ECR Repo
        repository = ecr.Repository.from_repository_arn(
        self,
        construct_id,
        repository_arn=container_repo)

        # ECS Cluster
        cluster = ecs.Cluster(self, "RecapAIApiCluster", vpc=vpc)

        # Fargate
        fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self, "FargateService",
            cluster=cluster,
            listener_port=80, # for ports other than 80, you need listner-port set to port and container_port set to port.  Currently we are port forwarding 80 to 8000
            desired_count=1, # sets desired host count for auto-scaling
            task_image_options=ecs_patterns.NetworkLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_ecr_repository(repository, tag="latest"),
                container_port=8000,  # for ports other than 80, you need listner-port set to port and container_port set to port
            )
        )

        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection = ec2.Port.tcp(8000),
            description="Allow http inbound from VPC"
        )

        # AutoScaling policy
        scaling = fargate_service.service.auto_scale_task_count(
            max_capacity=3, # sets max host count for auto-scaling
            min_capacity=1, # sets min host count for auto-scaling
        )
        scaling.scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=50,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60),
        )

        CfnOutput(
            self, "LoadBalancerDNS",
            value=fargate_service.load_balancer.load_balancer_dns_name
        )






    

