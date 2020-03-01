from simulator.node import Node
import json
import sys
import copy


# also implement Dijkstra’s Algorithm
class Link_State_Node(Node):
    def __init__(self, id):
        super().__init__(id)
        self.all_edges = {} # (A,B):latency
        self.edges_seq = {} # (A,B):seq
        self.seq = 0


    # Return a string
    def __str__(self):
        return str(self.id) + "\n"
        # return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link

        # store the link in graph
        if latency == -1 and neighbor in self.neighbors:
            # remove neighbor node
            self.neighbors.remove(neighbor)

            self.edges_seq.pop((self.id,neighbor))
            self.edges_seq.pop((neighbor, self.id))

            self.all_edges.pop((self.id,neighbor))
            self.all_edges.pop((neighbor, self.id))

            msg = json.dumps([self.id, neighbor, latency, self.seq])
            self.send_to_neighbors(msg)
            self.seq += 1


        else:
            old_latency = self.all_edges.get((self.id, neighbor))
            self.all_edges.update({(self.id, neighbor): latency})
            self.all_edges.update({(neighbor, self.id): latency})

            if neighbor not in self.neighbors:
                self.neighbors.append(neighbor)

                msg = json.dumps([self.id, neighbor, latency, self.seq])
                self.send_to_neighbors(msg)

                # share link to neighbors
                for M,N in self.all_edges.keys():
                    ltc = self.all_edges.get((M,N))
                    msg = json.dumps([M, N, ltc, self.seq])
                    self.send_to_neighbor(neighbor,msg)

                self.seq += 1


            else:

                if old_latency != latency:
                    # share link to neighbors
                    msg = json.dumps([self.id, neighbor, latency, self.seq])
                    self.send_to_neighbors(msg)
                    self.seq += 1

        print(self.id,"get all_edges:",len(self.all_edges.keys()))
        print("------")


    # Fill in this function
    def process_incoming_routing_message(self, m):

        new_node1, new_node2, ltc, seq = json.loads(m)

        # update current edge latency
        if not self.edges_seq.get((new_node1, new_node2)):
            self.edges_seq.update({(new_node1,new_node2): seq})
            self.edges_seq.update({(new_node2,new_node1): seq})

            self.all_edges.update({(new_node2,new_node1): ltc})
            self.all_edges.update({(new_node1, new_node2): ltc})

            if ltc == -1:
                self.all_edges.pop((new_node2,new_node1))
                self.all_edges.pop((new_node1, new_node2))

            self.send_to_neighbors(m)

        elif seq > self.edges_seq[(new_node1,new_node2)]:
            self.edges_seq.update({(new_node1,new_node2): seq})
            self.edges_seq.update({(new_node2,new_node1): seq})

            self.all_edges.update({(new_node2,new_node1): ltc})
            self.all_edges.update({(new_node1, new_node2): ltc})

            if ltc == -1:
                self.all_edges.pop((new_node2,new_node1))
                self.all_edges.pop((new_node1, new_node2))

            self.send_to_neighbors(m)

        else:
            return


    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # initialize the unvisited Q
        dist = {}
        prev = {}
        graph_nodes = self.get_graph_nodes()
        for v in graph_nodes:
            dist[v] = sys.maxsize
            prev[v] = None
        dist[destination] = 0
        for vt in self.get_neighbors(destination):
            dist[vt] = self.all_edges.get((vt,destination))
            prev[vt] = destination
        Q = graph_nodes[:]
        Q.remove(destination)

        while Q:
            # find the minimum values in Q
            min_dist = sys.maxsize
            min_node = Q[0]

            for ver in Q:
                if dist.get(ver) < min_dist:
                    min_dist = dist.get(ver)
                    min_node = ver
            Q.remove(min_node)
            nb_of_mincode = self.get_neighbors(min_node)
            if nb_of_mincode:
                for nei in nb_of_mincode:
                    alt = dist[min_node] + self.all_edges.get((min_node,nei))
                    if alt < dist[nei]:
                        dist[nei] = alt
                        prev[nei] = min_node
            else: continue

        # print("dist[]:",dist)
        # print("prev[]:",prev)

        return prev.get(self.id)

    def get_neighbors(self,node):
        ls = []
        # print("all edges keys:", self.all_edges.keys())
        for M,N in self.all_edges.keys():
            if M == node and N not in ls:
                ls.append(N)
            if N == node and M not in ls:
                ls.append(M)
        return ls

    def get_graph_nodes(self):
        q = []
        for M,N in self.all_edges.keys():
            if M not in q:
                q.append(M)
            if N not in q:
                q.append(N)

        return q
