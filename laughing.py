from popmatches import mexp, matches
import random


class FSM(object):
    output = ''

    def __init__(self, name, initial, final, arcs):
        self.name = name
        self.initial = initial
        self.final = final
        self.arcs = arcs
        self.finished = False

    def exit_from_fsm(self):
        raise Exception('exiting from FSM')

    def traverse_network(self, start_node):
        for arc in self.arcs:
            if matches(arc, [start_node, mexp('?to'), mexp('?symbol')]):
                if to == self.final:
                    self.output += symbol
                    self.finished = True
                    self.exit_from_fsm()
                elif symbol == '#' and random.random() < 0.8:
                    self.traverse_network(to)
                elif symbol != '#':
                    self.output += symbol
                    self.traverse_network(to)

    def traverse(self):
        try:
            self.traverse_network(self.initial)
        except:
            pass
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
