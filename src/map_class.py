import random
import numpy as np

class Map:
    def __init__(self,num_node):
        self.num_node = num_node

        self.graph = self._make_map(num_node)
        self.node_list = list(self.graph.keys())

        self.congestions ={}
        for u, info in self.graph.items():
            for v, _ in info["edges"]:
                self.congestions[(u, v)] = 1.0

    def _make_map(self,num_node):
        node_map = {}
        for i in range(num_node):
            name = str(i)
            node_map[name] = {
            'pos': (random.randint(0, 100), random.randint(0, 100)),
            'edges': []
        }

        for i in range(num_node):
            targets = random.sample([str(j) for j in range(num_node) if i != j], 2)
            for t in targets:
            # 座標から距離（コスト）を計算
                p1 = node_map[str(i)]['pos']
                p2 = node_map[t]['pos']
                cost = int(((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5)
                node_map[str(i)]['edges'].append((t, cost))
            
        return node_map
    def update(self):
        """【動的更新】毎ステップ、すべての道の混雑度をじわじわ変化させる"""
        for edge in self.congestions.keys():
            current_c = self.congestions[edge]

            # 連続値トリック：前の混雑度を95%引き継ぎつつ、±0.05のランダム変化を与える
            next_c = (current_c * 0.95) + np.random.uniform(-0.05, 0.05)

            # 1.0（スイスイ）〜 3.0（大渋滞）の間に収める
            self.congestions[edge] = max(1.0, min(3.0, next_c))

    def get_real_distance(self, u, v):
        """【コスト取得】A*やロボットが使う、渋滞を掛け算した『実際の移動コスト』を返す"""
        base_dist = 0
        # 元々の距離（コスト）を graph から探す
        for neighbor, weight in self.graph[str(u)]["edges"]:
            if neighbor == str(v):
                base_dist = weight
                break

        # 現在の混雑度（倍率）をかけて、体感の「重さ」にする
        multiplier = self.congestions.get((str(u), str(v)), 1.0)
        return base_dist * multiplier

    def get_pos(self, node):
        """【座標取得】ノードの座標 (x, y) を返すヘルパー（A*や可視化で使用）"""
        return self.graph[str(node)]["pos"]