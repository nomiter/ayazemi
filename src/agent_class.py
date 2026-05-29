class Agent:
    def __init__(self, attitude, agent_id, start_node, vehicle_speed):
        self.attitude = attitude  # A*アルゴリズム関数
        self.agent_id = agent_id
        self.current_node = start_node
        self.speed = vehicle_speed
        self.time_to_next_node = 0.0
        self.next_node = None
        self.status = "IDLE"
        self.path = []
        self.assigned_order = None

    def assign_order(self, order, sim_map):
        """管制塔から新しいオーダーを割り当てられた時の初期経路計算"""
        self.assigned_order = order
        self.status = "TO_PICKUP"

        if self.attitude is not None:
            path_to_pickup = self.attitude(sim_map, self.current_node, order.origin)
            self.path = path_to_pickup[1:]

    def update(self, sim_map):
        if self.status == "IDLE":
            return
        
        # 【状態1】エッジ移動中のカウントダウン
        if self.next_node is not None:
            self.time_to_next_node -= 1.0
            if self.time_to_next_node <= 0:
                self.current_node = self.next_node
                self.next_node = None
                
                # 📍 交差点（ノード）に到着した瞬間、最新の渋滞を反映してA*を再計算（リプランニング）
                if self.status == "TO_PICKUP" and self.current_node != self.assigned_order.origin:
                    path_to_pickup = self.attitude(sim_map, self.current_node, self.assigned_order.origin)
                    self.path = path_to_pickup[1:]
                elif self.status == "TO_DELIVERY" and self.current_node != self.assigned_order.destination:
                    path_to_delivery = self.attitude(sim_map, self.current_node, self.assigned_order.destination)
                    self.path = path_to_delivery[1:]

        # 【状態2】次のノードへの移動開始（実際の距離 / 速度 でリアルな所要時間を計算）
        if self.next_node is None and self.path:
            self.next_node = self.path.pop(0)
            real_distance = sim_map.get_real_distance(self.current_node, self.next_node)
            self.time_to_next_node = real_distance / self.speed

        # 【状態3】目的地にジャスト到着した瞬間のステータス遷移（集荷完了・配達完了）
        if self.next_node is None and not self.path:
            if self.status == "TO_PICKUP" and self.current_node == self.assigned_order.origin:
                self.status = "TO_DELIVERY"
                if self.attitude is not None:
                    path_to_delivery = self.attitude(sim_map, self.current_node, self.assigned_order.destination)
                    self.path = path_to_delivery[1:]

            elif self.status == "TO_DELIVERY" and self.current_node == self.assigned_order.destination:
                self.assigned_order.status = "COMPLETED"
                self.status = "IDLE"
                self.assigned_order = None