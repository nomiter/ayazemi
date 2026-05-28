import matplotlib.pyplot as plt
class Center:
    def __init__(self,map,agents,order):
        self.map = map
        self.agents = agents
    
    def visualize(self,agents,order):
        plt.figure(figsize=(20,15))
        plt.subplot()