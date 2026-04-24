import heapq # 効率的なノード選択のために必須

def dijkstra(edge_map, start_node, goal_node):
    """
    edge_map: { '0': {'pos': (x, y), 'edges': [('1', cost), ...]}, ... }
    """
    # 1. 初期化
    # 距離の辞書: {'0': 0, '1': inf, ...}
    distances = {node: float('inf') for node in edge_map}
    distances[start_node] = 0
    
    # 優先度付きキュー: (現在のコスト, 現在のノード)
    pq = [(0, start_node)]
    
    # 経路復元用: どのノードから来たかを記録
    previous_nodes = {node: None for node in edge_map}

    while pq:
        current_cost, u = heapq.heappop(pq)

        # すでに確定済みの距離より大きい場合はスキップ
        if current_cost > distances[u]:
            continue
            
        # 2. 隣接ノードの探索
        for v, weight in edge_map[u]['edges']:
            distance = current_cost + weight
            
            # 3. 距離の更新
            if distance < distances[v]:
                distances[v] = distance
                previous_nodes[v] = u
                heapq.heappush(pq, (distance, v))
                
# --- 変更点: 結果を表示しやすく整理 ---
    print(f"=== ダイクストラ法 計算結果 (始点: {start_node}) ===")
    
    # 経路復元処理
    path = []
    curr = goal_node
    while curr is not None:
        path.append(curr)
        curr = previous_nodes[curr]
    path.reverse()
    
    # 出力整形
    for node in sorted(edge_map.keys(), key=lambda x: int(x)):
        cost = distances[node]
        cost_str = "到達不能" if cost == float('inf') else f"{cost}"
        print(f"ノード {node:2} | 最小コスト: {cost_str:>6}")
        print("-" * 25)
        
    print(f"\n[最短経路]: {' -> '.join(path) if path[0] == start_node else '到達不可'}")
    print("============================================")
    
    return distances, previous_nodes, path