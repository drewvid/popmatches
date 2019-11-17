from popmatches import mexp, matches
import random
from pprint import pprint

A__ = mexp("==")

class FSTN(object):

    output = []

    def __init__(self, name, arcs, abbreviations, tape):
        self.name = name
        self.arcs = arcs
        self.network = arcs
        self.abbreviations = abbreviations
        self.tape = tape
        self.finished = False

    def exit_from_fstn(self):
        raise Exception('exiting from FSM')

    def initial_nodes(self):
        global v, A__
        matches(self.network, [A__, ['Initial', mexp('??v')], A__])
        return v

    def final_nodes(self):
        global v, A__
        matches(self.network, [A__, ['Final', mexp('??v')], A__])
        return v

    def valid_move(self, label, s):
        global A__
        return matches(self.abbreviations, [A__, [label, 'abbreviates', A__, s, A__], A__])

    def get_transitions(self, node):
        global newnode, label
        pattern = ['From', node, 'to', mexp('?newnode'), 'by', mexp('?label')]
        return [(newnode, label) for entry in self.network if matches(entry, pattern)]

    def recognise_move(self, label, tape):
        if tape is not [] and self.valid_move(label, tape[0]):
            self.output.append((label, tape[0]))
            return tape[1:]
        elif label == '#':
            return tape
        return None

    def recognise_next(self, node, tape):
        if tape == [] and node in self.final_nodes():
            self.finished = True
            self.exit_from_fstn()

        for newnode, label  in self.get_transitions(node):
            newtape = self.recognise_move(label, tape)
            if newtape is not None:
                self.recognise_next(newnode, newtape)

    def recognise(self):
        try:
            for node in self.initial_nodes():
                self.recognise_next(node, self.tape)
        except:
            pass
        self.pr()

    def pr(self):
        if self.finished:
            pprint(self.output)
        else:
            print("FSM did not complete!")


if __name__ == '__main__':

    arcs = [['Initial', 1],
            ['Final', 9],
            ['From', 1, 'to', 3, 'by', 'NP'],
            ['From', 1, 'to', 2, 'by', 'DET'],
            ['From', 2, 'to', 3, 'by', 'N'],
            ['From', 3, 'to', 4, 'by', 'BV'],
            ['From', 4, 'to', 5, 'by', 'ADV'],
            ['From', 4, 'to', 5, 'by', '#'],
            ['From', 5, 'to', 6, 'by', 'DET'],
            ['From', 5, 'to', 7, 'by', 'DET'],
            ['From', 5, 'to', 8, 'by', '#'],
            ['From', 6, 'to', 6, 'by', 'MOD'],
            ['From', 6, 'to', 7, 'by', 'ADJ'],
            ['From', 7, 'to', 9, 'by', 'N'],
            ['From', 8, 'to', 8, 'by', 'MOD'],
            ['From', 8, 'to', 9, 'by', 'ADJ'],
            ['From', 9, 'to', 4, 'by', 'CNJ'],
            ['From', 9, 'to', 1, 'by', 'CNJ']]

    abbreviations = [['NP', 'abbreviates', 'kim', 'sany', 'lee'],
                     ['DET', 'abbreviates', 'a', 'the', 'her'],
                     ['N', 'abbreviates', 'consumer', 'man', 'woman'],
                     ['BV', 'abbreviates', 'is', 'was'],
                     ['CNJ', 'abbreviates', 'and', 'or'],
                     ['ADJ', 'abbreviates', 'happy', 'stupid'],
                     ['MOD', 'abbreviates', 'very'],
                     ['ADV', 'abbreviates', 'often', 'always', 'sometimes']]

    tape = 'kim was a consumer and lee was stupid'.split()

    myfstn = FSTN('english_1', arcs, abbreviations, tape)
    myfstn.recognise()
