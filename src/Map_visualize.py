import matplotlib.pyplot as plt


def map_visualize(node_map):
    plt.figure(figsize=(10,8)) # 引数に入れるのも視野
    drawn_edges = set()

    for node, info in node_map.items():
        x1,y1 = info['pos']

        plt.scatter(x1,y1,color='royalblue',s = 600,zorder =3)
        plt.text(x1,y1,node,fontsize=15,ha = 'center',va = 'center')

        for neighbor, weight in info['edges']:
            if neighbor in node_map:
                x2, y2 = node_map[neighbor]['pos']
            
                # ソートして重複描画を防ぐ
                edge_key = tuple(sorted((node, neighbor)))
                if edge_key not in drawn_edges:
                    plt.plot([x1, x2], [y1, y2], color='gray', linestyle='--', alpha=0.6, zorder=1)
                
                    # エッジの重みを表示（中間地点）
                    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                    plt.text(mid_x, mid_y, str(weight), fontsize=10, color='darkred', 
                            bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1), zorder=2)
                    drawn_edges.add(edge_key)

    plt.title('Network Visualization (Nodes and Edges)', fontsize=16)
    plt.xlabel('X coordinate')
    plt.ylabel('Y coordinate')
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.show()