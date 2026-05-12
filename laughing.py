from popmatches import mexp, matches
import random


class FSM(object):
    """
    Simple Finite State Machine for string generation using popmatches.
    """

    def __init__(self, name, initial, final, arcs):
        self.name = name
        self.initial = initial
        self.final = final
        self.arcs = arcs
        self.finished = False
        self.output = ''

    def exit_from_fsm(self):
        raise Exception('exiting from FSM')

    def traverse_network(self, start_node, current_str):
        """Recursively traverse the network, accumulating the generated string."""
        global to, symbol
        for arc in self.arcs:
            if matches(arc, [start_node, mexp('?to'), mexp('?symbol')]):
                if to == self.final:
                    self.output = current_str + symbol
                    self.finished = True
                    self.exit_from_fsm()
                elif symbol == '#' and random.random() < 0.8:
                    self.traverse_network(to, current_str)
                elif symbol != '#':
                    self.traverse_network(to, current_str + symbol)

    def traverse(self):
        """Start the FSM traversal from the initial node."""
        try:
            self.traverse_network(self.initial, '')
        except Exception as e:
            if str(e) == 'exiting from FSM':
                # Normal termination signal
                pass
            else:
                print(f"Error during FSM traversal: {e}")
        self.pr()

    def pr(self):
        if self.finished:
            print(self.output)
        else:
            print("FSM did not complete!")


if __name__ == '__main__':

    arcs = [[1, 2, 'h'],
            [2, 3, 'a'],
            [3, 1, '#'],
            [3, 4, '!']]

    start_node = 1
    final_node = 4

    myfsm = FSM('to laugh', start_node, final_node, arcs)

    myfsm.traverse()
