import math
import matplotlib.pyplot as plt
from IPython.display import clear_output  # 画面をリアルタイムに書き換えるためのモジュール


def visualize_simulation(node_map, agents, active_orders, current_time):
    # 描画サイズ（Jupyter上で見やすい大きさ）
    plt.figure(figsize=(12, 10))
    drawn_edges = set()

    # --------------------------------------------------
    # ① ベースとなるマップ（ノードとエッジ）の描画
    # --------------------------------------------------
    for node, info in node_map.items():
        x1, y1 = info["pos"]

        # 基本ノードは薄い青丸
        plt.scatter(x1, y1, color="lightblue", s=500, zorder=2, edgecolors="gray")
        plt.text(
            x1,
            y1,
            node,
            fontsize=12,
            ha="center",
            va="center",
            weight="bold",
            zorder=3,
        )

        for neighbor, weight in info["edges"]:
            if neighbor in node_map:
                x2, y2 = node_map[neighbor]["pos"]

                # 一方通行（有向グラフ）が分かりやすいように矢印（annotate）にするのがおすすめです
                edge_key = (node, neighbor)
                if edge_key not in drawn_edges:
                    # 矢印で道を描画
                    plt.annotate(
                        "",
                        xy=(x2, y2),
                        xytext=(x1, y1),
                        arrowprops=dict(
                            arrowstyle="->",
                            color="gainsboro",
                            linestyle="--",
                            lw=1.5,
                        ),
                        zorder=1,
                    )
                    drawn_edges.add(edge_key)

    # --------------------------------------------------
    # ② アクティブなオーダー（荷物位置と配達先）のハイライト
    # --------------------------------------------------
    for oid, order in active_orders.items():
        if order["status"] == "PENDING":
            # まだ誰も拾っていないオーダーの積み込み地を「黄色」で強調
            ori_x, ori_y = node_map[order["origin"]]["pos"]
            plt.scatter(
                ori_x,
                ori_y,
                facecolors="none",
                edgecolors="orange",
                s=800,
                linewidths=3,
                zorder=2,
            )
            plt.text(
                ori_x,
                ori_y + 4,
                f"🎁{oid}",
                color="darkorange",
                fontsize=9,
                ha="center",
            )

    # --------------------------------------------------
    # ③ 【目玉機能】エージェントの現在位置をリアルタイム計算して描画
    # --------------------------------------------------
    # ロボットごとに色を変えるためのカラーマップ
    colors = ["red", "blue", "green", "purple", "orange"]

    for idx, ag in agents.items():
        color = colors[idx % len(colors)]

        # パターンA: ノード上に完全に停止・待機している場合
        if ag.next_node is None:
            ag_x, ag_y = node_map[ag.current_node]["pos"]

        # パターンB: エッジを移動中の場合（残り時間から、今エッジの何％にいるかを計算！）
        else:
            x1, y1 = node_map[ag.current_node]["pos"]
            x2, y2 = node_map[ag.next_node]["pos"]

            # エッジの総距離を取得
            distance = 0
            for neighbor, dist in node_map[ag.current_node]["edges"]:
                if neighbor == ag.next_node:
                    distance = dist
                    break

            # 総移動時間 ＝ 距離 ÷ 速度
            total_time = distance / ag.speed

            # 現在の進捗率 (0.0 ～ 1.0) を計算
            if total_time > 0:
                progress = 1.0 - (ag.time_to_next_node / total_time)
                progress = max(0.0, min(1.0, progress))  # 安全対策
            else:
                progress = 1.0

            # 内分点の座標を計算（これでエッジの途中を滑らかに動きます！）
            ag_x = x1 + (x2 - x1) * progress
            ag_y = y1 + (y2 - y1) * progress

        # エージェントを「星型（★）」または大きな丸でプロット
        plt.scatter(
            ag_x,
            ag_y,
            color=color,
            marker="*",
            s=400,
            zorder=5,
            edgecolors="black",
            label=f"{ag.agent_id} ({ag.status})",
        )
        # ロボットの名前を表示
        plt.text(
            ag_x,
            ag_y - 4,
            f"🤖{ag.agent_id}\n({ag.status})",
            color=color,
            fontsize=10,
            ha="center",
            weight="bold",
            zorder=6,
        )

    # グラフの装飾
    plt.title(
        f"AMR Simulation (Time: {current_time}s | Orders: {len(active_orders)}件)",
        fontsize=16,
    )
    plt.grid(True, linestyle=":", alpha=0.5)
    plt.legend(loc="upper right")

    # Jupyterの画面を更新するために show して終了
    plt.show()