from dataclasses import dataclass, field
from typing import Generic, List, Union

from pytree.Binarytree._type_hint import CT


@dataclass(order=True, slots=True)
class BST_Node(Generic[CT]):
    '''
    - a basic binary search tree node
    - has a double reference, i.e the child and parent
      both references each other
    P.S: NOT to be used independantly as is,
         should use the 'Tree' class as the interface
    '''

    value: CT = None
    parent: 'BST_Node' = field(default=None, repr=False, compare=False)
    left: 'BST_Node' = field(default=None, repr=False, compare=False)
    right: 'BST_Node' = field(default=None, repr=False, compare=False)

    @property
    def grandparent(self) -> Union['BST_Node', None]:
        '''get the parent of the parent of the node, if any'''
        try:
            return self.parent.parent
        except AttributeError:
            return None

    @property
    def uncle(self) -> Union['BST_Node', None]:
        '''get the uncle of the parent of the node, if any'''
        try:
            return self.grandparent.right \
                if self.parent is self.grandparent.left \
                else self.grandparent.left

        except AttributeError:
            return None

    @property
    def sibling(self) -> Union['BST_Node', None]:
        '''get the sibling of the node, if any'''
        try:
            # in case the node calling this has been deleted
            if self.parent.left is None:
                return self.parent.right
            elif self.parent.right is None:
                return self.parent.left

            return self.parent.left \
                if self is self.parent.right \
                else self.parent.right
        except AttributeError:
            return None

    @property
    def depth(self) -> int:
        depth = 0
        current_node = self
        while current_node.parent:
            current_node = current_node.parent
            depth += 1
        return depth

    @property
    def height(self) -> int:
        '''recursively get the height of the node'''
        def traversal_counter(node) -> int:
            if node is None:
                return -1
            return 1 + max(traversal_counter(node.left),
                           traversal_counter(node.right))

        return traversal_counter(self)

    @property
    def is_leaf(self) -> bool:
        return not self.right and not self.left

    @property
    def is_branch(self) -> bool:
        return self.right or self.left

    def update(self, **kwargs) -> None:
        [setattr(self, k, v) for k, v in kwargs.items()]

    def traverse_node(self, key: str = 'in') -> List['BST_Node']:
        '''
        returns a list all the items in the binary tree in the given order type
        in-order  ['in']: from min-to-max
        pre-order ['pre']: root node as the beginning, from left to right
        post-order ['post']: root node as the end, from left to right
        level-order ['lvl']: from top-to-bottom, left-to-right, kinda like BST
        '''
        def inorder_traversal(node: 'BST_Node', path: list) -> List[CT]:
            if node.left:
                inorder_traversal(node.left, path)
            path.append(node)
            if node.right:
                inorder_traversal(node.right, path)
            return path

        def postorder_traversal(node: 'BST_Node', path: list) -> List[CT]:
            if node.left:
                postorder_traversal(node.left, path)
            if node.right:
                postorder_traversal(node.right, path)
            path.append(node)
            return path

        def preorder_traversal(node: 'BST_Node', path: list) -> List[CT]:
            path.append(node)
            if node.left:
                preorder_traversal(node.left, path)
            if node.right:
                preorder_traversal(node.right, path)
            return path

        def levelorder_traversal(node: 'BST_Node', path: list) -> List[CT]:
            from collections import deque

            stack = deque([node])

            while stack != deque([]):
                node = stack.popleft()
                path.append(node)

                if node.left:
                    stack.append((node.left))
                if node.right:
                    stack.append((node.right))

            return path

        traversing_option = {
            'in': inorder_traversal,
            'post': postorder_traversal,
            'pre': preorder_traversal,
            'lvl': levelorder_traversal
        }
        if key not in traversing_option:
            raise ValueError(f'{key} given is not a valid option')

        return traversing_option[key](self, [])

    def insert_node(self, value: CT) -> None:
        '''insert a value into the binary tree'''
        self._insert_node(value)

    def _insert_node(self, value: CT) -> Union[None, 'BST_Node']:
        '''internal function of the binary tree where the recursions happen'''
        if value == self.value:
            return None

        if value < self.value:
            if self.left is None:
                self.left = self.__class__(value, parent=self)
                return self.left
            else:
                return self.left._insert_node(value)

        elif value > self.value:
            if self.right is None:
                self.right = self.__class__(value, parent=self)
                return self.right
            else:
                return self.right._insert_node(value)

    def find_node(self, value: CT) -> Union[None, 'BST_Node']:
        '''search for the given value in the binary tree'''
        if self.value is None:
            return None
        elif self.value == value:
            return self
        if self.left and value < self.value:
            return self.left.find_node(value)
        elif self.right and value > self.value:
            return self.right.find_node(value)

    def find_gt_node(self, value: CT) -> Union['BST_Node', None]:
        '''
        find the node with the closest value
        that's less than or equal to the given value
        '''
        if value < self.value:
            if self.left and value <= self.left.value:
                return self.left.find_gt_node(value)
            else:
                return self
        else:
            if self.right:
                return self.right.find_gt_node(value)
            return None

    def find_lt_node(self, value: CT) -> Union['BST_Node', None]:
        '''
        find the node with the closest value
        that's less than or equal to the given value
        '''
        if value > self.value:
            if self.right and value >= self.right.value:
                return self.right.find_lt_node(value)
            else:
                return self
        else:
            if self.left:
                return self.left.find_lt_node(value)
            return None

    def find_le_node(self, value: CT) -> Union['BST_Node', None]:
        '''
        find the node with the closest value
        that's less than or equal to the given value
        '''

        # if the leaf node has been reached, but the value is still smaller
        # than the smallest value in the tree
        if not (self.left and self.right) and value < self.value:
            return None

        if self.value <= value and \
           (self.right is None or self.right.value > value):
            return self

        if self.value >= value:
            return self.left.find_lt_node(value)
        else:
            return self.right.find_lt_node(value)

    def find_ge_node(self, value: CT) -> Union['BST_Node', None]:
        '''find the node with the closest value that's >= the given value'''

        # if the leaf node has been reached, but the value is still bigger
        # than the biggest value in the tree
        if not (self.left and self.right) and value > self.value:
            return None

        # if the node's value is greater or equal to the given value
        if self.value >= value and (self.left is None or self.left.value < value):
            return self

        if self.value <= value:
            return self.right.find_gt_node(value)
        else:
            return self.left.find_gt_node(value)

    def find_min_node(self) -> 'BST_Node':
        '''find the minimum value relative to a specific node in the tree'''
        if self.left is None:
            return self
        return self.left.find_min_node()

    def find_max_node(self) -> 'BST_Node':
        '''find the maximum value relative to a specific node in the tree'''
        if self.right is None:
            return self
        return self.right.find_max_node()

    def delete_node(self, node_to_delete: 'BST_Node') -> None:
        '''remove the given vaue from the binary tree'''
        node_to_delete._delete_node()

    def _delete_node(self) -> 'BST_Node':
        '''
        recursively going down the chain of nodes until
        a node with only 1 child or no child is found
        then, perform necceesarily steps to make the node obselete

         CASE 1: if the node have 0 child

          if the node is not the root node,
          -> check the role of the node(right child/left child)
          --> then, destroy the node's relationship with its parent
          if the node is the root node, set its value to None
        _____________________________________________________________________________________________
         CASE 2: if the node have 2 child

          --> get the child with the min value relative to the right child /
              get the child with the max value relative to the left child
              and recursively going down the chain from that child's position
              until a succesful deletion

          this will ensure that the chosen child fits the parent's position
          (doesn't violate any BST invariants)
            - if the child is the one with the max value
              relative to the left child
              - replacing the parent with its value guarentees that
                all the child that's on the left has 'smaller' value than 'him'
                and all the child on the right has bigger value than him
                [otherwise insertion has gone wrong to begin with]

            * Vice versa for the other case
              (if the child is the one with the min value
               relative to the right child)

         NOTE TO SELF:
         consider the following example:
         - the node to be deleted is the root node [7]

           - the successor node in this case would be [8],
             since it is the one with the min value
             relative to the right child of the root node

             - [8] will be 'promoted' as the new root node / swap its value
                   with the node to be deleted

               (This essentially 'deletes' the node
                since it has its original value replaced,
                even though that the underlying object of the node
                is still the same
                {i.e no new node has been created in the process}
                )

               - the < _delete_node > function will then be
                 called upon the original [8] node,
                 in which the CASE 3 will be activated
                 since there only ever will be at most 1 child for [8]
                 or else [8] wouldn't have been the min node
                    7
                 /      \
                3        9
              /   \n    /  \
             1     5   8    10
            / \n  / \n  \
           0   2 4   6   8.5


                    8
                 /      \
                3        9
              /   \n    /  \
             1     5   8.5  10
            / \n  / \n
           0   2 4   6

        __________________________________________________________________________________________________________________________

         CASE 3: if the node only have 1 child

          --> check the child's relationship with the node

              if the node has a parent (i.e not the root node),
          ----> then, create a parent-child relationship
                between the node's parent and the child
                with respect to the child's relationship with the node
                (right child/left child)

              if the node does not have a parent (i.e is a root node)
          ----> then, swap entires with the child node
         '''

        # CASE 1: node have 0 child
        if self.left is None and self.right is None:
            if self.parent:
                if self.parent.left == self:
                    self.parent.left = None
                else:
                    self.parent.right = None
            else:
                self.value = None

            return self

        # CASE 2: node have 2 child
        elif self.left and self.right:
            successor_node = self.right.find_min_node()
            self.value = successor_node.value
            return successor_node._delete_node()

        # CASE 3: node has 1 child
        else:
            child_node = self.left if self.left else self.right

            # if the node is not the root node
            if self.parent:

                # rewire the relationship
                child_node.parent = self.parent
                if self.parent.left == self:
                    self.parent.left = child_node
                else:
                    self.parent.right = child_node

            # if the node is the root node
            else:

                # swap identity with the child node
                self.update(
                    parent=child_node.parent,
                    left=child_node.left,
                    right=child_node.right,
                    value=child_node.value
                )

                if child_node.right:
                    child_node.right.parent = self
                if child_node.left:
                    child_node.left.parent = self

                # get rid of the cyclic reference after the identity swap
                self.parent = None

            return child_node

    def _rotate_left(self) -> None:
        """
        Rotates left:

        Y:  node
        X:  node's right child
        T2: possible node's right child's left child (maybe None)
        P:  possible parent (maybe None) of Y

              p                               P
              |                               |
              x                               y
             / \n     left Rotation          /  \
            y   T3   < - - - - - - -        T1   x
           / \n                                 / \
          T1  T2                              T2  T3

        the right_child of Y becomes T2
        the left_child of X becomes Y
        the right_child/left_child of P becomes X, depends on X's role
        """
        parent_node = self.parent
        right_node = self.right
        self.right = right_node.left

        # set the parent of the T2 to Y if T2 exists
        if right_node.left:
            right_node.left.parent = self

        # set the Y as X's left_child
        right_node.left = self
        # set Y's parent to X
        self.parent = right_node
        # set X's parent to P (Y's original parent)(maybe None)
        right_node.parent = parent_node

        if parent_node:
            # set the role of X based of the role of Y (right_child/left_child)
            if parent_node.right == self:
                parent_node.right = right_node
            else:
                parent_node.left = right_node

    def _rotate_right(self) -> None:
        """
        Rotates right:

        Y:  node
        X:  node's left_child
        T2: node's left_child's right_child
        P:  possible parent (maybe None) of Y
              p                           P
              |                           |
              y                           x
             / \n     Right Rotation     /  \
            x   T3   - - - - - - - >    T1   y
           / \n                             / \
          T1  T2                          T2  T3

        the left_child of Y becomes T2
        the right_child of X becomes Y
        the right_child/left child of P becomes X, depends on X's role
        """
        parent_node = self.parent
        left_node = self.left
        self.left = left_node.right

        # set the parent of the T2 to Y if T2 exists
        if left_node.right:
            left_node.right.parent = self

        # set the Y as X's right_child
        left_node.right = self
        # set Y's parent to X
        self.parent = left_node
        # set X's parent to P (Y's original parent) (maybe None)
        left_node.parent = parent_node

        if parent_node:
            # set the role of X based of the role of Y (right_child/left_child)
            if parent_node.left == self:
                parent_node.left = left_node
            else:
                parent_node.right = left_node

    def get_root(self) -> 'BST_Node':
        '''
        used to get the root of the tree
        an acccessory function, totally unccessary,
        just thought that it'd make things a lil tider
        '''
        node = self
        while node.parent:
            node = node.parent
        return node
