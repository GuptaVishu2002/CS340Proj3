from simulator.node import Node
import copy
import json


class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.dv = {}
        self.direct_link_cost = {}
        self.neighbors_dv_set = {}
        self.neighbors_dv_seq = {}
        self.seq = 0
        # self.total = [self.id, self.dv, self.seq]
    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        # print(neighbor)

        if latency == -1 and neighbor in self.neighbors:

            self.neighbors.remove(neighbor)
            self.direct_link_cost.pop(str(neighbor))
            self.dv.pop(str(neighbor))
            self.neighbors_dv_set.pop(neighbor)
        else:
            if neighbor not in self.neighbors:
                self.neighbors.append(neighbor)                                # add a new neighbor in to self.neighbors
                # self.dv.update({neighbor: []})
                # self.neighbors_dv.update({neighbor: {}})
            # print(self.neighbors)
            self.direct_link_cost.update({str(neighbor): [latency, neighbor]})       # update the direct link cost
        # print("node:", self.id," direct cost:",self.direct_link_cost)
        # print('direct', self.direct_link_cost)
        candidate_dv = copy.deepcopy(self.direct_link_cost)               # use direct link as candidate DV at first
        # print('candidate', candidate_dv)
        for i in self.neighbors:                                          # find neighbors' DV
            if i in self.neighbors_dv_set.keys():
                for j in self.neighbors_dv_set[i]:                        # neighbor i's DV
                    # j = int(m)
                    if (j not in candidate_dv) and (int(j) != self.id) and (self.id not in self.neighbors_dv_set[i][j][1:]):     # neighbor i's DV has a destination that isn't my neighbor and that's not myself.
                        # print('direct',self.direct_link_cost)
                        candidate_dv.update({j: [0,0]})                   # add this destination and cost to my candidate DV
                        candidate_dv[j][0] = self.neighbors_dv_set[i][j][0] + self.direct_link_cost[str(i)][0]
                        candidate_dv[j][1:] = [i] + self.neighbors_dv_set[i][j][1:]
                    elif (int(j) != self.id) and (self.id not in self.neighbors_dv_set[i][j][1:]) :                               # neighbor i's DV has a destination that is also my neighbor.
                        if ((self.direct_link_cost[str(i)][0]+self.neighbors_dv_set[i][j][0]) < candidate_dv[j][0]) \
                                and self.id not in self.neighbors_dv_set[i][j][1:]:                                     # compare the cost and update my candidate DV
                            candidate_dv[j][0] = self.neighbors_dv_set[i][j][0] + self.direct_link_cost[str(i)][0]
                            candidate_dv[j][1:] = [i] + self.neighbors_dv_set[i][j][1:]
        if self.dv != candidate_dv:                                       # if my DV changes, I update it and send it to my neighbors
            # print('self', self.dv)
            # print('candidate', candidate_dv)
            self.dv = candidate_dv
            # msg =[self.id, self.dv, self.seq]
            msg = json.dumps([self.id, self.dv, self.seq])
            self.seq += 1
            # print('msg',self.id, ":", msg)
            self.send_to_neighbors(msg)
        # self.send_to_neighbor(neighbor, "hello")
        # print(self.id,':',self.dv)

    # Fill in this function
    def process_incoming_routing_message(self, m):
        new_dv_node, new_dv, seq = json.loads(m)
        # print("m",m)
        # print('this node', self.id)
        # print('seq',seq)
        if new_dv_node not in self.neighbors_dv_seq:
            self.neighbors_dv_seq.update({new_dv_node: seq})
            self.neighbors_dv_set.update({new_dv_node: new_dv})
        elif seq > self.neighbors_dv_seq[new_dv_node]:
            self.neighbors_dv_seq.update({new_dv_node: seq})
            self.neighbors_dv_set.update({new_dv_node: new_dv})
        else:
            # print('late')
            return
        # print(self.id, self.neighbors_dv)

        candidate_dv = copy.deepcopy(self.direct_link_cost)
        # print('direct',self.direct_link_cost)
        # print('neighbor dv set', self.neighbors_dv_set)
        # print('candidate',candidate_dv)
        for i in self.neighbors:
            if i in self.neighbors_dv_set.keys():
                for j in self.neighbors_dv_set[i]:
                    # j = int(m)
                    if (j not in candidate_dv) and (int(j) != self.id) and (self.id not in self.neighbors_dv_set[i][j][1:]):
                        # print('direct', self.direct_link_cost)
                        candidate_dv.update({j: [0, 0]})
                        candidate_dv[j][0] = self.neighbors_dv_set[i][j][0] + self.direct_link_cost[str(i)][0]
                        candidate_dv[j][1:] = [i] + self.neighbors_dv_set[i][j][1:]

                    elif (int(j) != self.id) and (self.id not in self.neighbors_dv_set[i][j][1:]):
                        # print(i,j)
                        # print(self.direct_link_cost[i][0] + self.neighbors_dv[i][j][0])
                        # print(candidate_dv[j][0])
                        if ((self.direct_link_cost[str(i)][0] + self.neighbors_dv_set[i][j][0]) < candidate_dv[j][0]) \
                                and self.id not in self.neighbors_dv_set[i][j][1:]:
                            candidate_dv[j][0] = self.neighbors_dv_set[i][j][0] + self.direct_link_cost[str(i)][0]
                            candidate_dv[j][1:] = [i] + self.neighbors_dv_set[i][j][1:]
        if self.dv != candidate_dv:
            # print('self',self.dv)
            # print('candidate',candidate_dv)
            self.dv = candidate_dv
            msg = json.dumps([self.id, self.dv, self.seq])
            # msg = [self.id, self.dv, self.seq]
            self.seq += 1
            # print(self.id, ":", msg)
            self.send_to_neighbors(msg)
            # print('neighbors',self.neighbors)
            # print('send',msg)

        # print(self.id, ':', self.dv)

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        return self.dv[str(destination)][1]
        # return -1
