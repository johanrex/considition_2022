import json


class Solution:
    def __init__(self, recycle_refund_choice: bool, bag_price: float, refund_amount: float, bagType: int, map_name: str, orders: list[int]):
        self.mapName: str = map_name
        self.recycleRefundChoice: bool = recycle_refund_choice
        self.bagPrice: float = bag_price
        self.refundAmount: float = refund_amount
        self.bagType: int = bagType
        self.orders: list[int] = orders

    def toJSON(self, indent=None):
        return json.dumps(self, default=lambda o: o.__dict__, indent=indent)

    @staticmethod
    def fromJSON(json_str: str):
        d = json.loads(json_str)
        s = Solution(
            map_name=d["mapName"],
            recycle_refund_choice=d["recycleRefundChoice"],
            bag_price=d["bagPrice"],
            refund_amount=d["refundAmount"],
            bagType=d["bagType"],
            orders=d["orders"],
        )

        return s
