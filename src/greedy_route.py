import heapq
import math

def greedy_best_first(edge_map, start_node, goal_node):
    def get_h(u):
        pos_u = edge_map[u]['pos']
        pos_g = edge_map[goal_node]['pos']
        return math.hypot(pos_u[0] - pos_g[0], pos_u[1] - pos_g[1])

    visited = {node: False for node in edge_map}
    previous_nodes = {node: None for node in edge_map}
    pq = [(get_h(start_node), start_node)]
    
    while pq:
        _, u = heapq.heappop(pq)
        
        if visited[u]:
            continue
        visited[u] = True
        
        if u == goal_node:
            break
            
        for v, weight in edge_map[u]['edges']:
            if not visited[v]:
                previous_nodes[v] = u
                heapq.heappush(pq, (get_h(v), v))
                
    # --- 経路復元とコスト計算 ---
    path = []
    total_cost = 0
    curr = goal_node
    
    # ゴールからスタートまで遡る
    while curr is not None:
        path.append(curr)
        # 次のノード（親ノード）を取得
        parent = previous_nodes[curr]
        if parent is not None:
            # 親から自分へのエッジの重みを探して加算
            for neighbor, weight in edge_map[parent]['edges']:
                if neighbor == curr:
                    total_cost += weight
                    break
        curr = parent
        
    path.reverse()
    
    is_reached = (len(path) > 0 and path[0] == start_node)
    
    print(f"=== Greedy Best-First Search 結果 (始点: {start_node} -> 終点: {goal_node}) ===")
    print(f"[最短経路]: {' -> '.join(path) if is_reached else '到達不可'}")
    print(f"[経路コスト]: {total_cost if is_reached else 'N/A'}")
    print("=====================================================================")
    
    return path, total_cost