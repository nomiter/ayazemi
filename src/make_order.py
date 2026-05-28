import random
import numpy as np

ST_PENDING = "PENDING"
ST_ASSIGNED = "ASSIGNED"
ST_COMPLETED = "COMPLETED"

def make_order(num_node,current_time,deadtime,order_id):
    rng = np.random.default_rng()
    nodes = rng.choice(num_node, size=2, replace=False)

    return {
        "order_id": order_id,
        "generation_time": current_time,
        "origin": int(nodes[0]),
        "destination": int(nodes[1]),
        "deadline": current_time + deadtime,
        "status": ST_PENDING,
    }