import heapq
import math

def a_star(edge_map, start_node, goal_node):
    """
    edge_map: { '0': {'pos': (x, y), 'edges': [('1', cost), ...]}, ... }
    """
    # ゴールまでの予測距離 (h(n)) を計算するヒューリスティック関数(未来の推定価値)
    def get_h(u):
        pos_u = edge_map[u]['pos']
        pos_g = edge_map[goal_node]['pos']
        return math.hypot(pos_u[0] - pos_g[0], pos_u[1] - pos_g[1])

    # 1. 初期化
    distances = {node: float('inf') for node in edge_map} # g(n)（現在までの確定価値　無限にしておく）
    distances[start_node] = 0
    
    # 優先度付きキュー: (f(n), g(n), current_node)
    # f(n) = g(n) + h(n)
    pq = [(get_h(start_node), 0, start_node)]
    
    previous_nodes = {node: None for node in edge_map}

    while pq:
        _, current_g, u = heapq.heappop(pq)

        # ゴール判定
        if u == goal_node:
            break

        if current_g > distances[u]:
            continue
            
        # 2. 隣接ノードの探索
        for v, weight in edge_map[u]['edges']:
            g_v = current_g + weight
            
            # 3. コスト更新
            if g_v < distances[v]:
                distances[v] = g_v
                f_v = g_v + get_h(v) # A* の肝：実コスト + 予測コスト
                previous_nodes[v] = u
                heapq.heappush(pq, (f_v, g_v, v))
                
    # 4. 経路復元
    path = []
    curr = goal_node
    while curr is not None:
        path.append(curr)
        curr = previous_nodes[curr]
    path.reverse()
    
    # 出力
    print(f"=== A* アルゴリズム 結果 (始点: {start_node} -> 終点: {goal_node}) ===")
    print(f"[最短経路]: {' -> '.join(path) if len(path) > 0 and path[0] == start_node else '到達不可'}")
    print(f"[合計コスト]: {distances[goal_node]}")
    print("==========================================================")
    
    return path