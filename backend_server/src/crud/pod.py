from datetime import datetime, timezone

import yaml
from fastapi import HTTPException
from kubernetes import client, config

from backend_server.src.models.instance import Instance
from backend_server.src.utils.my_enum import PodStatus

config.load_kube_config('/root/.kube/config')  # 로컬 실행 시에는 주석 처리 필수
pod_client = client.CoreV1Api()


class PodService:
    @staticmethod
    async def create_pod(instance, template):
        with open("/robot-simulator/src/pod-template.yaml", "r") as f:
            pod = yaml.safe_load(f)

        pod_name = f"instance-{instance.simulation_id}-{instance.id}"
        pod_label = {"agent-type": template.type.lower()}

        pod["metadata"]["name"] = pod_name
        pod["metadata"]["labels"] = pod_label
        pod["spec"]["containers"][0]["name"] = pod_name

        pod_namespace = instance.pod_namespace
        pod_client.create_namespaced_pod(namespace=pod_namespace, body=pod)
        return pod_name

    @staticmethod
    async def get_pod_status(pod_name, namespace):
        pod = pod_client.read_namespaced_pod(namespace=namespace, name=pod_name)
        return pod.status.phase

    @staticmethod
    async def get_pod_image(pod_name, namespace):
        pod = pod_client.read_namespaced_pod(namespace=namespace, name=pod_name)
        return pod.spec.containers[0].image if pod.spec.containers else ""

    @staticmethod
    async def get_pod_age(pod_name, namespace):
        pod = pod_client.read_namespaced_pod(namespace=namespace, name=pod_name)
        creation_time = pod.metadata.creation_timestamp
        time_difference = datetime.now(timezone.utc) - creation_time

        total_seconds = int(time_difference.total_seconds())
        days, remainder = divmod(total_seconds, 86400)  # 1일 = 86400초
        hours, remainder = divmod(remainder, 3600)  # 1시간 = 3600초
        minutes, seconds = divmod(remainder, 60)  # 1분 = 60초

        time_units = [("d", days), ("h", hours), ("m", minutes), ("s", seconds)]
        return next(f"{value}{unit}" for unit, value in time_units if value > 0)

    @staticmethod
    async def get_pod_label(pod_name, namespace):
        pod = pod_client.read_namespaced_pod(namespace=namespace, name=pod_name)
        if pod.metadata.labels:
            label = next(iter(pod.metadata.labels.items()))
            return str(label[1])
        return ""

    @staticmethod
    async def delete_pod(pod_name, namespace):
        pod_client.delete_namespaced_pod(name=pod_name, namespace=namespace)

    @staticmethod
    async def create_namespace(simulation_id: int):
        name = f"simulation-{simulation_id}"
        metadata = client.V1ObjectMeta(name=name)
        namespace = client.V1Namespace(metadata=metadata)
        pod_client.create_namespace(namespace)
        return name

    @staticmethod
    async def delete_namespace(simulation_id: int):
        pod_client.delete_namespace(name=f"simulation-{simulation_id}")

    @staticmethod
    async def get_pod_ip(instance: Instance):
        pod = pod_client.read_namespaced_pod(name=instance.pod_name, namespace=instance.pod_namespace)
        return pod.status.pod_ip

    async def is_pod_ready(self, instance: Instance):
        pod_status = await self.get_pod_status(instance.pod_name, instance.pod_namespace)
        return pod_status == PodStatus.RUNNING.value

    async def check_pod_status(self, instance: Instance):
        pod_status = await self.get_pod_status(instance.pod_name, instance.pod_namespace)
        code = await self.get_pod_status_code(pod_status)
        if code != 200:
            raise HTTPException(status_code=code, detail=f"Pod Status: {pod_status}")

    @staticmethod
    async def get_pod_status_code(pod_status):
        """Pod 상태에 따른 상태 코드 반환"""
        status_code_map = {
            "Pending": 520,
            "ContainerCreating": 521,
            "Running": 200,
            "Error": 500,
            "ImagePullBackOff": 522,
            "ErrImagePull": 523,
            "CrashLoopBackOff": 524,
            "Unknown": 530,
        }
        return status_code_map.get(pod_status)
