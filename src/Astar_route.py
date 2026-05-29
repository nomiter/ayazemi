import heapq
import math

def a_star(sim_map, start_node, goal_node):
    """クラス連動版 A* アルゴリズム"""
    start_node = str(start_node)
    goal_node = str(goal_node)

    # 0. ヒューリスティック関数（直線距離）
    def heuristic(u, g):
        pos_u = sim_map.get_pos(u)
        pos_g = sim_map.get_pos(g)
        return math.hypot(pos_u[0] - pos_g[0], pos_u[1] - pos_g[1])

    # 1. 初期化
    distances = {node: float('inf') for node in sim_map.node_list}
    distances[start_node] = 0

    # 優先度付きキュー: (f(n), g(n), current_node)
    queue = [(heuristic(start_node, goal_node), 0, start_node)]
    parent_map = {}

    # 2. 探索ループ
    while queue:
        current_f, current_g, u = heapq.heappop(queue)

        if u == goal_node:
            break

        if current_g > distances[u]:
            continue

        # 隣接ノードを探索
        for v, _ in sim_map.graph[u]["edges"]:
            # ★ここが進化！Mapクラスから『現在の渋滞補正後の距離コスト』を取得する
            weight = sim_map.get_real_distance(u, v)
            new_g = current_g + weight

            if new_g < distances[v]:
                distances[v] = new_g
                parent_map[v] = u
                f_cost = new_g + heuristic(v, goal_node)
                heapq.heappush(queue, (f_cost, new_g, v))

    # 3. 経路の復元
    if goal_node not in parent_map and start_node != goal_node:
        return []

    path = []
    curr = goal_node
    while curr != start_node:
        path.append(curr)
        curr = parent_map[curr]
    path.append(start_node)
    path.reverse()

    return path