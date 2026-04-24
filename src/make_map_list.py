import random

def make_map(num_node):
    """
    {
        '0': {'pos': (x, y), 'edges': [('1', cost), ...]},
        '1': {'pos': (x, y), 'edges': [...]},
    }
    """
    node_map = {}
    
    # 1. 各ノードの初期化（座標をランダムに設定）
    for i in range(num_node):
        name = str(i)
        node_map[name] = {
            'pos': (random.randint(0, 100), random.randint(0, 100)),
            'edges': []
        }
        
    # 2. エッジ（繋がり）を適当に生成する例
    # 実際にはここでノード間の距離を計算してedgesを埋める
    for i in range(num_node):
        # 自分以外のノードをランダムに2つ選んで繋ぐ
        targets = random.sample([str(j) for j in range(num_node) if i != j], 2)
        for t in targets:
            # 座標から距離（コスト）を計算
            p1 = node_map[str(i)]['pos']
            p2 = node_map[t]['pos']
            cost = int(((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5)
            node_map[str(i)]['edges'].append((t, cost))
            
    return node_map

