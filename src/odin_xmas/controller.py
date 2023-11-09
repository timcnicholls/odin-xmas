import logging

from odin.adapters.parameter_tree import ParameterTree

from .tree import RGBXmasTree

class XmasController():

    def __init__(self):
        
        self._enable = False
        self.tree = RGBXmasTree()
        self.param_tree = ParameterTree({
            'enable': (lambda: self._enable, self.set_enable),
        })

    def initialize(self):
        
        self.set_enable(self._enable)

    def cleanup(self):
        
        self.tree.off()
        self.tree.close()

    def get(self, path):
        """Get values from the parameter tree.

        This method returns values from parameter tree to the adapter.

        :param path: path to retrieve from tree
        """
        return self.param_tree.get(path)

    def set(self, path, data):
        """Set values in the parameter tree.

        This method sets values in the parameter tree. 

        :param path: path of data to set in the tree
        :param data: data to set in tree
        """
        # Update values in the tree at the specified path
        self.param_tree.set(path, data)

        # Return updated values from the tree
        return self.param_tree.get(path)        

    def set_enable(self, value):

        value = bool(value)
        if value:
            self.tree.on()
        else:
            self.tree.off()

        self._enable = value