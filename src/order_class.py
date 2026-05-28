import numpy as np


class Order:

    def __init__(self, order_id, current_time, deadtime, num_node):
        """初期化: 乱数の抽選からデータの格納までを自動で行う設計図"""
        # 1. 元のコードの乱数ロジックをそのまま使用
        rng = np.random.default_rng()
        nodes = rng.choice(num_node, size=2, replace=False)

        # 2. インスタンスのポケット（プロパティ）にデータを仕舞う
        self.order_id = order_id
        self.generation_time = current_time
        self.deadline = current_time + deadtime
        self.status = "PENDING"

        # ★【ここが超重要！】
        # 抽選された数値を、ここで str() を使って文字列（'1' や '18'）に変換して保存！
        # これにより、外側のコードは型を一切気にする必要がなくなります。
        self.origin = str(nodes[0])
        self.destination = str(nodes[1])

    def to_dict(self):
        """【便利機能】自分自身のデータを「辞書形式」に一発変換して返すメソッド"""
        return {
            "order_id": self.order_id,
            "generation_time": self.generation_time,
            "origin": self.origin,
            "destination": self.destination,
            "deadline": self.deadline,
            "status": self.status,
        }