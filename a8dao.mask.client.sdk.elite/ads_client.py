import httpx


class AdsClient:
    base_url = "http://localhost:50325"

    def create(self):
        return httpx.post(
            self.base_url + "/api/v1/user/create",
            json={"group_id": "0", "user_proxy_config": {"proxy_soft": "no_proxy"}},
        ).json()

    def exists(self, user_id: str):
        return (
            len(
                httpx.get(
                    self.base_url + "/api/v1/user/list",
                    params={"user_id": user_id},
                ).json()["data"]["list"]
            )
            > 0
        )

    def stop(self, user_id: str):
        return httpx.get(
                    self.base_url + "/api/v1/browser/stop",
                    params={"user_id": user_id},
                ).json()

if __name__ == "__main__":
    client = AdsClient()
    res=client.create()
    print(res)
    # res = client.exists("3590")
    # print(res)
