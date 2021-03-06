from typing import Generic, Union, Tuple, List
import pickle

from pytree.Binarytree._type_hint import CT, BSN
from pytree.Binarytree.Node import BST_Node


class BinaryTree(Generic[CT]):
    '''
    - This is the base class for all binary search tree
    - it acts as an interface for the node classes
      and shouldn't be instantiated on its own

    all binary search tree variations should inherit this class
    to obtain all the necessary interface functions
    '''
    _node_type: BSN = None

    def __init__(self):
        if self._node_type is None:
            raise TypeError("Cannot instantiate base class.")

        self.root: BST_Node = self._node_type()

    @property
    def dtype(self):
        '''returns the data type of that a tree contains'''
        if self.root is None:
            return None
        return type(self.root.value)

    @property
    def height(self) -> int:
        return self.root.height

    @property
    def is_complete(self) -> bool:
        '''
        check whether the tree is complete,
        -> i.e all nodes of the tree either has 2 child or no child
        '''

        def traversal_check(node: BSN) -> bool:
            # keep going down the chain of nodes
            # until the leftmost/rightmost node has been reached
            # then, return True, as leaf nodes has no child nodes
            if node is None:
                return True

            left_check = traversal_check(node.left)
            right_check = traversal_check(node.right)

            # check whether the node is 'complete'
            # i.e: whether is has both child or no child
            completeness_check = (node.left and node.right) or \
                                 (node.left is None and node.right is None)

            return left_check and right_check and completeness_check

        return traversal_check(self.root)

    @property
    def is_perfect(self) -> bool:
        '''
        check whether the tree is perfect
        -> i.e each branch of the tree has the same height
        '''

        def traversal_check(node: BSN) -> Tuple[bool, int]:
            # keep going down the chain of nodes
            # until the leftmost/rightmost node has been reached
            # return True, as leaf nodes has 0 child and are balanced
            if node is None:
                return (True, -1)

            left_check = traversal_check(node.left)
            right_check = traversal_check(node.right)

            # check whether the left & right node is perfect
            # and whether the height the node is perfect
            perfectness_check = (left_check[0] and right_check[0]
                                 and abs(left_check[1] - right_check[1]) == 0)  # noqa

            return (perfectness_check, 1 + max(left_check[1], right_check[1]))

        return traversal_check(self.root)[0]

    @property
    def is_empty(self) -> bool:
        return self.root.value is None

    @classmethod
    def fill_tree(cls, values: List[CT]) -> 'BinaryTree':
        '''generates a binary tree with all the values from a list'''
        new_bst = cls()
        for value in values:
            new_bst.insert(value)
        return new_bst

    @classmethod
    def load_pickle(cls, filename: str) -> 'BinaryTree':
        tree = cls()
        with open(filename, 'rb') as f:
            tree.extend(pickle.load(f))
        return tree

    def pickle(self, filename: str) -> None:
        with open(filename, 'wb') as f:
            pickle.dump(self.traverse(), f, pickle.HIGHEST_PROTOCOL)

    def extend(self, values: List[CT]) -> None:
        '''generates a binary tree with all the values from a list'''
        for value in values:
            self.insert(value)

    def insert(self, value: CT) -> None:
        '''add a node with the given value into the tree'''
        if self.root.value is None:
            self.root.value = value
        else:
            self.root.insert_node(value)

        if self.root.parent is not None:
            self.root = self.root.get_root()

    def delete(self, value: CT) -> None:
        '''remove the node that contains the specified value from the tree'''
        if self.root.value is None:
            raise ValueError(f'{value} is not in {self.__class__.__name__}')

        if not isinstance(value, type(self.root.value)):
            raise TypeError(f"tree does not contain value of type {type(value).__name__}")

        node_to_delete = self.root.find_node(value)

        if node_to_delete is None:
            raise ValueError(f'{value} is not in {self.__class__.__name__}')

        self.root.delete_node(node_to_delete)

        if self.root.parent is not None:
            self.root = self.root.get_root()

    def pop(self, value: CT = None, key: str = None) -> CT:
        '''get and delete the given value from the tree'''
        popping_options = {
            'val': self.find,
            'min': self.find_min,
            'max': self.find_max
        }

        if self.root.value is None:
            raise IndexError(
                f'trying to pop from an empty {type(self).__name__} tree')

        if key and key not in popping_options:
            raise ValueError(f'{key} given is not a valid option')

        if key and value:
            raise ValueError('only one of the arguements can be given')

        # default settings for the pop method
        popping_func = popping_options['min']

        if value:
            def popping_func():
                return popping_options['val'](value)  # noqa: E731
        elif key:
            popping_func = popping_options[key]

        found_val = popping_func()

        self.delete(found_val)

        return found_val

    def clear(self) -> None:
        self.root.left = None
        self.root.right = None
        self.root.value = None

    def traverse(self, key: str = 'in') -> List[Union[BSN, CT]]:
        '''
        returns list of all the items in the tree in the given order type
        in-order  ['in']: from min-to-max
        pre-order ['pre']: root node as the beginning, from left to right
        post-order ['post']: root node as the end, from left to right
        level-order ['lvl']: from top-to-bottom, left-to-right, kinda like BST
        '''
        if self.root.value is None:
            return []
        return [n.value for n in self.root.traverse_node(key)]

    def find(self, value: CT) -> CT:
        '''get the node with the given value'''
        if self.root.value is None:
            return None
        if not isinstance(value, type(self.root.value)):
            raise TypeError(f"tree does not contain value of type '{type(value).__name__}'")
        found_node = self.root.find_node(value)
        return found_node.value if found_node else None

    def find_lt(self, value: CT, **kwargs) -> CT:
        '''get the node with the given value'''
        if self.root.value is None:
            return None
        if not isinstance(value, type(self.root.value)):
            raise TypeError(f"tree does not contain value of type '{type(value).__name__}'")
        found_node = self.root.find_lt_node(value, **kwargs)
        return found_node.value if found_node else None

    def find_gt(self, value: CT, **kwargs) -> CT:
        '''find the node with the closest value that's > the given value'''
        if self.root.value is None:
            return None
        if not isinstance(value, type(self.root.value)):
            raise TypeError(f"tree does not contain value of type '{type(value).__name__}'")
        found_node = self.root.find_gt_node(value, **kwargs)
        return found_node.value if found_node else None

    def find_le(self, value: CT, **kwargs) -> CT:
        '''get the node with the given value'''
        if self.root.value is None:
            return None
        if not isinstance(value, type(self.root.value)):
            raise TypeError(f"tree does not contain value of type '{type(value).__name__}'")
        found_node = self.root.find_le_node(value, **kwargs)
        return found_node.value if found_node else None

    def find_ge(self, value: CT, **kwargs) -> CT:
        '''find the node with the closest value that's < the given value'''
        if self.root.value is None:
            return None
        if not isinstance(value, type(self.root.value)):
            raise TypeError(f"tree does not contain value of type '{type(value).__name__}'")
        found_node = self.root.find_ge_node(value, **kwargs)
        return found_node.value if found_node else None

    def find_max(self, **kwargs) -> CT:
        '''get the node with the maximum value in the tree'''
        if self.root.value is None:
            return None
        return self.root.find_max_node(**kwargs).value

    def find_min(self, **kwargs) -> CT:
        '''get the node with the minimum value in the tree'''
        if self.root.value is None:
            return None
        return self.root.find_min_node(**kwargs).value

    def __add__(self, other: Union[CT, 'BinaryTree']) -> 'BinaryTree':
        '''add this tree to another tree, omitting all repeated values'''
        if isinstance(other, type(self)):
            if self.dtype != other.dtype and not isinstance(
                    self.root.value, type(None)) and not isinstance(
                        other.root.value, type(None)):
                raise TypeError(
                    f"cannot add '{type(self).__name__}({self.dtype.__name__})' \
                      with '{type(other).__name__}({other.dtype.__name__})'")
            return type(self).fill_tree([val for val in self] + [val for val in other])

        try:
            return type(self).fill_tree(self.traverse()).insert(other)
        except TypeError:
            raise TypeError(
                f"cannot insert value of type '{other.__class__.__name__}' \
                  into '{self.__class__.__name__}({self.dtype.__name__})'")

    def __iadd__(self, other: Union[CT, 'BinaryTree']) -> 'BinaryTree':
        '''add this tree to another tree, omitting all repeated values'''
        if isinstance(other, type(self)):
            if self.dtype != other.dtype and not isinstance(
                    self.root.value, type(None)) and not isinstance(
                        other.root.value, type(None)):
                raise TypeError(
                    f"cannot add '{type(self).__name__}({self.dtype.__name__})' \
                      with '{type(other).__name__}({other.dtype.__name__})'")
            [self.insert(val) for val in other]
            return self

        try:
            self.insert(other)
            return self
        except TypeError:
            raise TypeError(
                f"cannot insert value of type '{other.__class__.__name__}' into \
                '{self.__class__.__name__}({self.dtype.__name__})'")

    def __sub__(self, other: Union[CT, 'BinaryTree']) -> 'BinaryTree':
        '''
        subtract this tree by another tree
        - only common values within both trees will be removed
        '''
        if isinstance(other, type(self)):
            if self.dtype != other.dtype and not isinstance(
                    self.root.value, type(None)) and not isinstance(
                        other.root.value, type(None)):
                raise TypeError(
                    f"cannot subtract {type(self).__name__}('{self.dtype.__name__}') from \
                      '{type(other).__name__}({other.dtype.__name__})'")
            return type(self).fill_tree(
                [val for val in self if val not in other])

        try:
            return type(self).fill_tree(self.traverse()).delete(other)
        except TypeError:
            raise TypeError(
                f"cannot delete value of type '{other.__class__.__name__}' from \
                '{self.__class__.__name__}({self.dtype.__name__})'")

    def __isub__(self, other: Union[CT, 'BinaryTree']) -> 'BinaryTree':
        '''
        subtract this tree by another tree
        - only common values within both trees will be removed
        '''
        if isinstance(other, type(self)):
            if self.dtype != other.dtype and not isinstance(
                    self.root.value, type(None)) and not isinstance(
                        other.root.value, type(None)):
                raise TypeError(
                    f"cannot subtract {type(self).__name__}('{self.dtype.__name__}') \
                    from '{type(other).__name__}({other.dtype.__name__})'")

            [self.delete(val) for val in other if val in self]
            return self

        try:
            self.delete(other)
            return self
        except TypeError:
            raise TypeError(
                f"cannot delete value of type '{other.__class__.__name__}' \
                from '{self.__class__.__name__}({self.dtype.__name__})'")

    def is_subset(self, other: 'BinaryTree') -> bool:
        for val in self:
            if val not in other:
                return False
        return True

    def is_superset(self, other: 'BinaryTree') -> bool:
        for val in other:
            if val not in self:
                return False
        return True

    def is_disjoint(self, other: 'BinaryTree') -> bool:
        for val in other:
            if val in self:
                return False
        return True

    def difference(self, other: 'BinaryTree') -> 'BinaryTree':
        return self - other

    def difference_update(self, other: 'BinaryTree') -> None:
        self -= other

    def intersection(self, other: 'BinaryTree') -> 'BinaryTree':
        common_val = [val for val in self if val in other]
        return self.fill_tree(common_val)

    def intersection_update(self, other: 'BinaryTree') -> None:
        common_val = [val for val in self if val in other]
        self.root = self.fill_tree(common_val).root

    def __getitem__(self, key):
        mod_key = len(self) - abs(key) if key < 0 else key

        if mod_key > len(self) - 1 or mod_key < 0:
            raise IndexError(f'{key} is out of range!')

        return self.traverse()[mod_key]

    def __setitem__(self, key, value):
        self.delete(self[key])
        self.insert(value)

    def __delitem__(self, key):
        self.delete(self[key])

    def __len__(self):
        return sum(1 for _ in self.traverse())

    def __iter__(self):
        yield from self.traverse()

    def __contains__(self, value: CT) -> bool:
        if self.root.value is None:
            return False
        return self.root.find_node(value)

    def __bool__(self) -> bool:
        return self.root.value is not None

    def __str__(self):
        return str(self.traverse())
