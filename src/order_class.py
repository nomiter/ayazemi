import numpy as np

class Order:
    def __init__(self, order_id, current_time, deadtime, num_node):
        """初期化: 乱数の抽選からデータの格納までを自動で行う"""
        rng = np.random.default_rng()
        nodes = rng.choice(num_node, size=2, replace=False)

        self.order_id = order_id
        self.generation_time = current_time
        self.deadline = current_time + deadtime
        self.status = "PENDING"
        
        # マップのキー（文字列）と完全に一致させるため、ここで強制的に文字列に変換
        self.origin = str(nodes[0])
        self.destination = str(nodes[1])

    def to_dict(self):
        """自分自身のデータを「辞書形式」に一発変換して返す（CSV保存用）"""
        return {
            "order_id": self.order_id,
            "generation_time": self.generation_time,
            "origin": self.origin,
            "destination": self.destination,
            "deadline": self.deadline,
            "status": self.status
        }

    @staticmethod
    def try_generate(current_time, deadtime, num_node, gen_prob, counter):
        """指定された確率に基づき、オーダーを自動生成して返すスタティックメソッド"""
        if np.random.rand() < gen_prob:
            oid = f"ORD_{counter:05d}"
            new_order = Order(
                order_id=oid,
                current_time=current_time,
                deadtime=deadtime,
                num_node=num_node
            )
            return new_order, counter + 1
        return None, counter