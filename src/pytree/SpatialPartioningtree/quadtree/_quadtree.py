from typing import Optional, List, Union, Tuple

from ..utils import is_inscribed, is_intersecting, split_box, BBox
from ..type_hints import UID

from ._quadnode import QuadNode


class QuadTree:

    def __init__(
        self,
        size: Tuple[int, int],
        max_depth: int = 12,
        auto_id: bool = False,
    ):
        self.bbox = BBox(0, 0, *size)
        self.auto_id = auto_id
        self.max_depth = int(max_depth)

        self._free_quad_node_index = -1
        self._num_quad_node_in_use = 1

        self.all_quad_node: List[QuadNode] = []
        self.all_quad_node.append(QuadNode())

        self.cleaned = True

    @property
    def num_quad_node(self):
        return len(self.all_quad_node)

    @property
    def num_quad_node_in_use(self):
        return self._num_quad_node_in_use

    @property
    def height(self) -> int:
        '''recursively get the height of the tree '''

        def traversal_counter(qnode_index) -> int:
            first_child = self.all_quad_node[qnode_index].first_child
            return 1 + max([
                traversal_counter(first_child + i) for i in range(4)
                if isinstance(first_child, int) and first_child != -1
            ],
                           default=0)

        return traversal_counter(0)

    @property
    def root(self):
        """returns the first quad node, for conveience"""
        return self.all_quad_node[0]

    # not good, implement the size option
    @classmethod
    def fill_tree(
        cls,
        bbox: "BBox",
        entities: Optional[Union[List[Tuple["UID", "BBox"]],
                                 List[Tuple["UID"]]]] = None,
        size: int = 0,
        capacity: Optional[int] = 1,
        auto_id: Optional[bool] = False,
    ) -> "QuadTree":

        if not any([entities, bbox]):
            raise ValueError(
                "requires at least 1 of the 2 arguements: 'size' & 'entities'")

        quadtree = cls(bbox, capacity, auto_id)

        [quadtree.insert(entity_data) for entity_data in entities]

        return quadtree

    def insert(self) -> None:
        raise NotImplementedError

    def get_bbox(self,
                 qnode: QuadNode,
                 index: Optional[bool] = False) -> Tuple[int, BBox]:
        """
        returns the bounding box of a quad node
        depending on the position of the quad node in the quad tree
        """
        if qnode == self.root:
            return (0, self.bbox)

        qnode_index = self.all_quad_node.index(qnode)
        quadrants = [(qnode_index - 1) % 4]

        # keep looping until the root node is reached
        # keep track of the quadrant of each node that has been traversed
        while qnode.parent_index != 0:
            quadrants.append((qnode.parent_index - 1) % 4)
            qnode = self.all_quad_node[qnode.parent_index]

        # split the main bounding box in order of the tracked quadrants
        # the quadrants list is not to be reversed
        # -> the node is traversed bottom-up
        # no need to keep a list of splitted bbox
        # -> the last bounding bbox will be the node's bbox
        tbbox = self.bbox
        for quadrant_index in quadrants:
            for ind, quad in enumerate(split_box(tbbox)):
                if ind == quadrant_index:
                    tbbox = quad

        return (qnode_index, tbbox)

    def find_quad_node(
        self,
        bbox: BBox,
        index: Optional[bool] = False
    ) -> Union[Tuple[QuadNode, BBox], Tuple[int, QuadNode, BBox]]:
        """
        returns a quad node that completely encompasses a given bbox
        the extra index paramter is also for convenience sake
        """
        to_process = [(0, self.bbox)]
        candidates = []

        while to_process:

            qindex, qbbox = to_process.pop()
            qnode = self.all_quad_node[qindex]

            if not qnode.in_use:
                continue

            candidates.append((qindex, qnode, qbbox))

            if qnode.is_leaf:
                continue

            for ind, quadrant in enumerate(split_box(qbbox)):
                # compare the area of the splitted quadrant and bbox
                # consider the quadrant if its area is >= the bbox's area
                if is_intersecting(bbox, quadrant) and is_inscribed(
                        bbox, quadrant):
                    to_process.append((qnode.first_child + ind, quadrant))

        target_qnode = min(candidates,
                           key=lambda qnode: qnode[2].w * qnode[2].h)
        return target_qnode if index else (target_qnode[1], target_qnode[2])

    def find_leaves(
        self,
        qnode: Optional[QuadNode] = None,
        bbox: Optional[BBox] = None,
        index: Optional[bool] = False,
    ) -> Union[List[Tuple[QuadNode, BBox]], List[Tuple[int, QuadNode, BBox]]]:
        """
        find the all the leaves that's encompassed by:
        - a quad node
        - a bounding bbox
        returns the found quad node, its bbox and its index (optional)
        """

        if not qnode and not bbox:
            raise ValueError(
                "at least one or the other is required, 'qnode' or 'bbox'")
        if qnode and bbox:
            raise ValueError(
                "only one or the other is allowed, 'qnode' or 'bbox'")

        if qnode:
            qindex, qbbox = self.get_bbox(qnode=qnode, index=True)

        if bbox:
            qindex, _, qbbox = self.find_quad_node(bbox=bbox, index=True)

        to_process = [(qindex, qbbox)]

        bounded_leaves = []

        while to_process:

            qindex, qbbox = to_process.pop()
            qnode = self.all_quad_node[qindex]

            if not qnode.in_use:
                continue

            if qnode.is_leaf:
                quad_data = (qindex, qnode, qbbox) if index else (qnode, qbbox)
                bounded_leaves.append(quad_data)
                continue

            for ind, quadrant in enumerate(split_box(qbbox)):
                if is_intersecting(qbbox, quadrant):
                    to_process.append((qnode.first_child + ind, quadrant))

        return bounded_leaves

    def clean_up(self) -> None:

        def clean_unused_qnode(qnode: QuadNode) -> None:
            # if the node is not in-use:
            # -> the node has been set free, the work is done
            # if the node is not an empty leaf node
            if not qnode.in_use or (qnode.is_leaf and qnode.total_entity > 0):
                return 0

            if qnode.is_branch:
                # recursively call this function upon all it's other 4 children
                # if all of its children have 0 entity nodes in it,
                # -> free all of its children and set it as an empty leaf
                # reset the node's first_child to 1 if its a root node,
                # -> or else it'll mess up future node allocations
                cindex = qnode.first_child
                if (sum(
                        clean_unused_qnode(self.all_quad_node[cindex + i])
                        for i in range(4)) == 4):
                    self.set_free_quad_node(cindex)

                    if qnode == self.root:
                        qnode.first_child = 1

            # return 1 since the node is an empty leaf
            return 1

        clean_unused_qnode(self.root)

    def set_branch(self, qnode: QuadNode, qindex: int):
        qnode.total_entity = -1

        self._num_quad_node_in_use += 4

        if self._free_quad_node_index == -1:
            # create 4 more quad node's and set the node's first child index
            qnode.first_child = len(self.all_quad_node)
            [
                self.all_quad_node.append(QuadNode(parent_index=qindex))
                for i in range(4)
            ]
            return

        # allocate that free node to the current node
        qnode.first_child = self._free_quad_node_index

        next_free_quad_node_index = self.all_quad_node[
            qnode.first_child].first_child

        for i in range(4):
            child_index = self._free_quad_node_index + i
            self.all_quad_node[child_index].update(first_child=-1,
                                                   total_entity=0,
                                                   parent_index=qindex)

        # reset the free node's index to the free node's child
        # which should either be -1 if there's no more free node
        # or another node's index
        self._free_quad_node_index = next_free_quad_node_index

    def set_free_quad_node(self, qindex: int) -> None:
        if (qindex - 1) % 4 != 0:
            raise ValueError(f"the liberation should happen to the \
                  first child not the '{(qindex - 1) % 4}' child")

        qnode = self.all_quad_node[qindex]
        parent_node = self.all_quad_node[qnode.parent_index]

        for i in range(4):
            self.all_quad_node[parent_node.first_child + i].set_free(
                self._free_quad_node_index)

        self._free_quad_node_index = qindex
        self._num_quad_node_in_use -= 4
        parent_node.first_child = -1
        parent_node.total_entity = 0
