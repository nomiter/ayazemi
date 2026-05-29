import random
import math
import numpy as np

class Map:
    def __init__(self, num_node):
        """初期化: ノード数を指定するだけでマップ生成と混雑度の初期化を自動完結"""
        self.num_node = num_node
        self.graph = self._make_map(num_node)
        self.node_list = list(self.graph.keys())

        # 動的な混雑度を管理する辞書 (初期値はすべて 1.0 = 渋滞なし)
        self.congestions = {}
        for u, info in self.graph.items():
            for v, _ in info["edges"]:
                self.congestions[(u, v)] = 1.0

    def _make_map(self, num_node):
        """クラス内部で実行される静的マップ生成ロジック"""
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
                # 座標から距離（コスト）を計算（三平方の定理）
                p1 = node_map[str(i)]['pos']
                p2 = node_map[t]['pos']
                cost = int(((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5)
                node_map[str(i)]['edges'].append((t, cost))
            
        return node_map

    def update(self):
        """毎ステップ呼び出され、すべてのエッジの混雑度をじわじわ変化させる（連続値ARモデル）"""
        for edge in self.congestions.keys():
            current_c = self.congestions[edge]
            # 前の状態を95%引き継ぎつつ、ランダムなノイズを加える
            next_c = (current_c * 0.95) + np.random.uniform(-0.05, 0.05)
            # 1.0（通常）〜 3.0（大渋滞）の間に丸める
            self.congestions[edge] = max(1.0, min(3.0, next_c))

    def get_real_distance(self, u, v):
        """A*やエージェントが使う、混雑度を反映した『実際の移動コスト（距離）』を返す"""
        base_dist = 0
        for neighbor, weight in self.graph[str(u)]["edges"]:
            if neighbor == str(v):
                base_dist = weight
                break

        multiplier = self.congestions.get((str(u), str(v)), 1.0)
        return base_dist * multiplier

    def get_pos(self, node):
        """指定したノードの座標 (x, y) を返すヘルパー"""
        return self.graph[str(node)]["pos"]