from simulator.node import Node


class Distance_Vector_Node(Node):
    def __init__(self, id):
        super().__init__(id)

    # Return a string
    def __str__(self):
        return "Rewrite this function to define your node dump printout"

    # Fill in this function
    def link_has_been_updated(self, neighbor, latency):
        # latency = -1 if delete a link
        # update your tables

        # send further messages to your neighbors

        pass

    # Fill in this function
    def process_incoming_routing_message(self, m):
        # call self.send_to_neighbors or self.send_to_neighbor

        # update your tables

        pass

    # Return a neighbor, -1 if no path to destination
    def get_next_hop(self, destination):
        # consult routing table

        # return next nod
        return -1
