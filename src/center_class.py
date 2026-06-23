import math
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import clear_output
from src.order_class import Order

class Center:
    def __init__(self, sim_map, agents, allocation_method="Euclid", log_filename="simulation_log_001.csv"):
        self.map = sim_map
        self.agents = agents
        self.allocation_method = allocation_method
        self.log_filename = log_filename
        self.active_orders = {}
        self.order_id_counter = 1

    def help_distance(self, node_a, node_b):
        """
        ノード間の距離を計算するヘルパーメソッド
        OSMの緯度経度に対応するため、Mapクラスが提供する座標、または実距離（コスト）を考慮
        """
        pos_a = self.map.get_pos(node_a)
        pos_b = self.map.get_pos(node_b)
        # OSM化に伴い、簡易的なユークリッド距離ではなく、
        # 必要に応じて実道路距離を返すようにMapクラス側と連携させるのが理想です。
        # 一旦、計算エラーを防ぐために元のロジックを維持、またはMapの実距離を参照。
        return math.hypot(pos_a[0] - pos_b[0], pos_a[1] - pos_b[1])

    def try_generate_order(self, current_time, deadtime, num_node, gen_prob):
        """確率に基づき、Orderクラスにオーダーの自動生成を委託・格納する"""
        new_ord, self.order_id_counter = Order.try_generate(
            current_time, deadtime, num_node, gen_prob, self.order_id_counter
        )
        if new_ord:
            self.active_orders[new_ord.order_id] = new_ord

    def allocation_order(self):
        """割当アルゴリズムに基づき、待機中ロボットに仕事を配分する"""
        if self.allocation_method == "Euclid":
            for oid, order in self.active_orders.items():
                if order.status == "PENDING":
                    best_agent = None
                    min_distance = float("inf")

                    for ag in self.agents.values():
                        if ag.status == "IDLE":
                            distance = self.help_distance(ag.current_node, order.origin)
                            if distance < min_distance:
                                min_distance = distance
                                best_agent = ag

                    if best_agent is not None:
                        best_agent.assign_order(order, self.map)
                        order.status = "ASSIGNED"

    def csv_save(self):
        """完了オーダーのCSV追記退避とメモリ解放"""
        completed_ids = [oid for oid, order in self.active_orders.items() if order.status == "COMPLETED"]
        if completed_ids:
            completed_list = []
            for oid in completed_ids:
                order_obj = self.active_orders.pop(oid)
                completed_list.append(order_obj.to_dict())

            df_to_save = pd.DataFrame(completed_list)
            df_to_save.to_csv(
                self.log_filename, mode="a",
                header=not os.path.exists(self.log_filename), index=False
            )

    def visualize(self, current_time):
        """Jupyter Notebook上への2画面分割マルチモーダルダッシュボード描画"""
        clear_output(wait=True)
        
        # 【修正】フォントの指定（rcParams）を完全に削除。システムのデフォルトを使用します。
        
        fig = plt.figure(figsize=(24, 12), dpi=100)

        # --- 左画面: マップビュー ---
        ax1 = plt.subplot(1, 2, 1)
        drawn_edges = set()

        # OSMはノード数が多いため、描画サイズを小さく調整 (s=500 -> s=30 など)
        # ※もしノード数が多すぎる場合は、あとで「エッジだけ描画する」モードに切り替えることも可能です。
        for node, info in self.map.graph.items():
            x1, y1 = info["pos"]
            ax1.scatter(x1, y1, color="lightblue", s=30, zorder=2, edgecolors="gray")
            # ノード名のテキスト（数字）も、OSMでは文字が重なって見えなくなるため一旦非表示、または小さく。
            # ax1.text(x1, y1, node, fontsize=8, ha="center", va="center", zorder=3)

            for neighbor, weight in info["edges"]:
                if neighbor in self.map.graph:
                    x2, y2 = self.map.graph[neighbor]["pos"]
                    edge_key = (node, neighbor)
                    if edge_key not in drawn_edges:
                        ax1.annotate("", xy=(x2, y2), xytext=(x1, y1),
                                     arrowprops=dict(arrowstyle="->", color="gainsboro", linestyle="--", lw=1.0),
                                     zorder=1)
                        drawn_edges.add(edge_key)

        # アクティブなオーダー（発生地点）の描画
        for oid, order in self.active_orders.items():
            if order.status == "PENDING":
                ori_x, ori_y = self.map.get_pos(order.origin)
                ax1.scatter(ori_x, ori_y, facecolors="none", edgecolors="orange", s=100, linewidths=2, zorder=2)
                # 【修正】「+ 4」などの大きな数値を足すと緯度経度がズレすぎるため、微小な値（またはズレなし）に変更
                ax1.text(ori_x, ori_y + 0.0002, f"🎁{oid}", color="darkorange", fontsize=9, ha="center")

        # エージェント（ロボット）の描画
        colors = ["red", "blue", "green", "purple", "orange"]
        for idx, ag in self.agents.items():
            color = colors[idx % len(colors)]
            if ag.next_node is None:
                ag_x, ag_y = self.map.get_pos(ag.current_node)
            else:
                x1, y1 = self.map.get_pos(ag.current_node)
                x2, y2 = self.map.get_pos(ag.next_node)

                distance = 0
                for neighbor, dist in self.map.graph[ag.current_node]["edges"]:
                    if neighbor == ag.next_node:
                        distance = dist
                        break

                total_time = distance / ag.speed
                progress = 1.0 - (ag.time_to_next_node / total_time) if total_time > 0 else 1.0
                progress = max(0.0, min(1.0, progress))
                ag_x = x1 + (x2 - x1) * progress
                ag_y = y1 + (y2 - y1) * progress

            ax1.scatter(ag_x, ag_y, color=color, marker="*", s=150, zorder=5, edgecolors="black")
            # 【修正】テキストのズレ（- 4）を緯度経度用に修正
            ax1.text(ag_x, ag_y - 0.0002, f"🤖{ag.agent_id}\n({ag.status})", color=color, fontsize=10, ha="center", weight="bold", zorder=6)

        ax1.set_title(f"AMR Map View (Active Orders: {len(self.active_orders)}件)", fontsize=14)
        ax1.grid(True, linestyle=":", alpha=0.5)

        # --- 右画面: エージェント＆オーダー詳細テキスト ---
        ax2 = plt.subplot(1, 2, 2)
        ax2.axis("off")

        info_text = "=========================================\n"
        info_text += "AGENT STATUS (エージェント運行状況)\n"
        info_text += "=========================================\n"
        for ag in self.agents.values():
            loc = f"ノード {ag.current_node}" if ag.next_node is None else f"{ag.current_node} ➔ {ag.next_node}"
            current_job = "なし"
            if ag.assigned_order is not None:
                current_job = f"{ag.assigned_order.order_id} (集荷:{ag.assigned_order.origin} ➔ 配達:{ag.assigned_order.destination})"
            info_text += f"・【{ag.agent_id}】 状態: {ag.status:<11} | 位置: {loc:<10} | 担当業務: {current_job}\n"
            if ag.path:
                info_text += f"    ┗ 予定ルート: {' ➔ '.join(ag.path)}\n"
        info_text += "\n"

        info_text += "=========================================\n"
        info_text += " 🎁 ACTIVE ORDERS (受注・未完了タスク一覧)\n"
        info_text += "=========================================\n"
        pending_orders = [o for o in self.active_orders.values() if o.status == "PENDING"]
        assigned_orders = [o for o in self.active_orders.values() if o.status == "ASSIGNED"]
        info_text += f" [待機中(PENDING)]: {len(pending_orders)}件 / [配送中(ASSIGNED)]: {len(assigned_orders)}件\n"
        info_text += "-----------------------------------------\n"

        if not self.active_orders:
            info_text += " 現在、アクティブなオーダーはありません。\n"
        else:
            for oid, order in self.active_orders.items():
                info_text += f"・【{oid}】 状態: {order.status:<9} | ルート: ノード {order.origin} ➔ {order.destination} | 期限: {order.deadline}s\n"

        # 【修正】fontfamily="sans-selifs" のタイポ（および指定自体）を削除してシンプルに
        ax2.text(0.02, 0.95, info_text, fontsize=12, va="top", ha="left",
                 bbox=dict(facecolor="whitesmoke", alpha=0.8, edgecolor="gainsboro", boxstyle="round,pad=1"))
        ax2.set_title("System Fleet Dashboard", fontsize=14, weight="bold")

        plt.suptitle(f"AMR System Simulation (Time: {current_time}s)", fontsize=18, weight="bold")
        plt.tight_layout()
        plt.show()

        plt.close(fig)