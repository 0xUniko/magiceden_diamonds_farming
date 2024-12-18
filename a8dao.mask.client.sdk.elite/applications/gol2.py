from api.local.web3.starknet import invoke
from config import config
from tools.logger import task_log

eth_contract = config["contract"]["starknet"]["eth"]
gol2_contract = "0x06a05844a03bb9e744479e3298f54705a35966ab04140d3d8dd797c1f6dc49d0"


class GoL2:
    def __init__(self, task_id: str) -> None:
        self.task_id = task_id

    def evolve(
        self,
        address: str,
        private_key: str,
        game_id: str = "0x7300100008000000000000000000000000",
    ):
        task_log(self.task_id, f"evolve game_id: {game_id}")
        res = invoke(
            gol2_contract, "evolve", {"game_id": game_id}, address, private_key
        )
        assert res["code"] == 0, f"evolve failed: {res['message']}"
        task_log(self.task_id, "evolve successfully")
