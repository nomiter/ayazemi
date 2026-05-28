class Agent:
    def __init__(self, attitude, agent_id, start_node, vehicle_speed):
        self.attitude = attitude # A*などのアルゴリズム関数
        self.agent_id = agent_id
        self.current_node = start_node
        self.speed = vehicle_speed
        self.time_to_next_node = 0.0
        self.next_node = None
        self.status = "IDLE"
        self.path = []
        self.assigned_order = None

    def assign_order(self, order, sim_map):
        self.assigned_order = order
        self.status = "TO_PICKUP"

        if self.attitude is not None:
            # 💡【修正】 order["origin"] から order.origin に変更
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
                
                # 【イベント駆動リプランニング】
                # 💡【修正】 辞書型からドット記法(.origin や .destination)に変更
                if self.status == "TO_PICKUP" and self.current_node != self.assigned_order.origin:
                    path_to_pickup = self.attitude(sim_map, self.current_node, self.assigned_order.origin)
                    self.path = path_to_pickup[1:]
                elif self.status == "TO_DELIVERY" and self.current_node != self.assigned_order.destination:
                    path_to_delivery = self.attitude(sim_map, self.current_node, self.assigned_order.destination)
                    self.path = path_to_delivery[1:]

        # 【状態2】次のノードへの移動開始
        if self.next_node is None and self.path:
            self.next_node = self.path.pop(0)
            real_distance = sim_map.get_real_distance(self.current_node, self.next_node)
            self.time_to_next_node = real_distance / self.speed

        # 【状態3】到着時のステータス遷移
        if self.next_node is None and not self.path:
            # 💡【修正】 self.assigned_order["origin"] から self.assigned_order.origin に変更
            if self.status == "TO_PICKUP" and self.current_node == self.assigned_order.origin:
                self.status = "TO_DELIVERY"
                
                if self.attitude is not None:
                    # 💡【修正】 self.assigned_order["destination"] から self.assigned_order.destination に変更
                    path_to_delivery = self.attitude(sim_map, self.current_node, self.assigned_order.destination)
                    self.path = path_to_delivery[1:]

            # 💡【修正】 self.assigned_order["destination"] から self.assigned_order.destination に変更
            elif self.status == "TO_DELIVERY" and self.current_node == self.assigned_order.destination:
                # 💡【修正】 self.assigned_order["status"] から self.assigned_order.status に変更
                self.assigned_order.status = "COMPLETED"
                self.status = "IDLE"
                self.assigned_order = None
                