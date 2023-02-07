import requests
import json

'''
TODO
endpoints = {
            "manifests": "{}/api/v1/applications/{}/manifests".format(argo_conf.ARGOCD_SERVER, self.app_name),
            "resource_events": "{}/api/v1/applications/{}/events".format(argo_conf.ARGOCD_SERVER, self.app_name),
            "patch_application": "{}/api/v1/applications/{}".format(argo_conf.ARGOCD_SERVER, self.app_name),
            "rollback": "{}/api/v1/applications/{}/rollback".format(argo_conf.ARGOCD_SERVER, self.app_name),
            "sync": "{}/api/v1/applications/{}/sync".format(argo_conf.ARGOCD_SERVER, self.app_name),
            "cluster_info": "{}/api/v1/clusters".format(argo_conf.ARGOCD_SERVER),
            "project_info": "{}/api/v1/projects".format(argo_conf.ARGOCD_SERVER),
        }
'''


class ArgoCDConf:
    ARGOCD_SERVER = ""
    AUTH_HEADER = {}

    @classmethod
    def __init__(cls, argocd_server: str, argocd_token: str) -> None:
        cls.ARGOCD_SERVER = argocd_server if argocd_server[-1] != "/" else argocd_server[:-1]
        cls.AUTH_HEADER = {
            "Authorization": "Bearer {}".format(argocd_token)
        }


class ResourceInfo:
    def __init__(self, argo_conf: ArgoCDConf, app_name: str):
        endpoint = "{}/api/v1/applications/{}/resource-tree".format(
            argo_conf.ARGOCD_SERVER, app_name)

        try:
            self.all_resources = requests.get(
                endpoint,
                headers=argo_conf.AUTH_HEADER,
                verify=False
            ).json()
        except Exception as e:
            raise e

    def get_by_name(self, name: str) -> dict:
        try:
            resources = self.all_resources['nodes']
            res = []
            for resource in resources:
                if name == resource['name']:
                    res.append(resource)
            return res
        except Exception as e:
            raise e

    def get_by_kind(self, kind: str) -> dict:
        try:
            resources = self.all_resources['nodes']
            res = []
            for resource in resources:
                if kind.lower() == resource['kind'].lower():
                    res.append(resource)
            return res

        except Exception as e:
            raise e

    def get_health_by_name(self, name: str) -> dict:
        try:
            resources = self.get_by_name(name=name)
            res = []
            for resource in resources:
                res.append(resource['health'])

            return res

        except Exception as e:
            raise e

    def get_health_by_kind(self, kind: str) -> dict:
        try:
            resources = self.get_by_kind(kind=kind)
            res = []
            if kind.lower() == "configmap" or kind.lower() == 'secret':

                # TODO: Logger
                print("{} kind does not have health information".format(kind))

            for resource in resources:
                res.append({resource['name']: resource['health']})

            return res
        except Exception as e:
            raise e


class ApplicationInfo:
    def __init__(self, argo_conf: ArgoCDConf, app_name: str):
        endpoint = "{}/api/v1/applications/{}".format(
            argo_conf.ARGOCD_SERVER, app_name)

        try:
            self.app_info = requests.get(
                url=endpoint,
                headers=argo_conf.AUTH_HEADER,
                verify=False
            ).json()

        except Exception as e:
            raise e

    def get_health_status(self) -> dict:
        app = self.app_info
        try:
            return app['status']['health']
        except Exception as e:
            raise e

    def get_sync_status(self) -> dict:
        app = self.app_info
        try:
            return app['status']['sync']
        except Exception as e:
            raise e


class ApplicationLogs:
    def __init__(self, argo_conf: ArgoCDConf, app_name: str) -> None:
        endpoint = "{}/api/v1/applications/{}/logs".format(
            argo_conf.ARGOCD_SERVER, app_name)
        try:
            raw_resp = requests.get(
                url=endpoint,
                headers=argo_conf.AUTH_HEADER,
                verify=False
            ).text
            self.all_logs = []
            for resp in raw_resp.splitlines():
                self.all_logs.append(json.loads(resp))

        except Exception as e:
            raise e
