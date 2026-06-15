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
    
    #def make_bus()


import random
import math
import numpy as np
import osmnx as ox

class Map2:
    def __init__(self, place_name, network_type="all"):
        """
        初期化: OSMから実際の道路ネットワークを取得し、既存システム用のマップ構造に変換。
        混雑度の自動初期化も完結させます。
        """
        self.graph = self._make_map_from_osm(place_name, network_type)
        self.node_list = list(self.graph.keys())
        self.num_node = len(self.node_list)

        # 動的な混雑度を管理する辞書 (初期値はすべて 1.0 = 渋滞なし)
        self.congestions = {}
        for u, info in self.graph.items():
            for v, _ in info["edges"]:
                self.congestions[(u, v)] = 1.0

    def _make_map_from_osm(self, place_name, network_type):
        """OSMデータをダウンロードし、既存の node_map 構造（文字列連番キー）にパースする内部ロジック"""
        print(f"OSMからデータを取得中: {place_name} ({network_type})...")
        # 1. OSMからグラフを取得
        G_osm = ox.graph_from_place(place_name, network_type=network_type)
        
        # 2. 扱いやすいように一度無向グラフの最大連結成分にする、あるいはそのまま利用
        # ※OSMの生ノードID（例: 28491048）を "0", "1", "2" のような文字列連番にマッピング
        osm_id_to_str_idx = {str(original_id): str(i) for i, original_id in enumerate(G_osm.nodes)}
        
        node_map = {}
        
        # 3. ノード座標の移植
        for original_id, data in G_osm.nodes(data=True):
            new_name = osm_id_to_str_idx[str(original_id)]
            # OSMの座標は(緯度y, 経度x)。元のコードのposに合わせて(x, y)の順、またはそのまま保持
            # ここでは一般的な(lng, lat)形式、あるいは必要に応じてメートル投影に変換も可能ですが、生値を入れます
            node_map[new_name] = {
                'pos': (data['x'], data['y']),
                'edges': []
            }

        # 4. エッジ（道路の繋がりと実距離）の移植
        for u, v, data in G_osm.edges(data=True):
            u_str = osm_id_to_str_idx[str(u)]
            v_str = osm_id_to_str_idx[str(v)]
            
            # OSMnxが自動計算した道路の実長さ（メートル単位）を取得。なければ0
            cost = int(data.get('length', 0))
            
            # 重複を避けてエッジを追加
            if (v_str, cost) not in node_map[u_str]['edges']:
                node_map[u_str]['edges'].append((v_str, cost))
                
            # もしOSMデータが一方通行で、シミュレーション上「双方向」にしたい場合は以下を有効化
            # if not data.get('oneway', False):
            #     if (u_str, cost) not in node_map[v_str]['edges']:
            #         node_map[v_str]['edges'].append((u_str, cost))
                    
        print(f"マップ生成完了: ノード数 {len(node_map)}")
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