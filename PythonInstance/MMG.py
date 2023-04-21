import pygame

pygame.init()


class Node:
    _nodes = {}

    @classmethod
    def node_exist(cls, node_id):
        if (node_id not in cls._nodes.keys()) or (cls.get_node(node_id) is None):
            return False
        return True

    def __init__(self, node_id, root_scene: str):
        if Node.node_exist(node_id):
            raise ValueError(f'The node id of {node_id} already exist.')
        Node._nodes[node_id] = self
        self.father_node_id: str = ""
        """节点的父节点的node id, 空串表示没有父节点"""
        self.son_node_ids: list[str] = []
        self.pos = (None, None)
        """节点在 **平面直角坐标系** 的坐标（基于 **Pygame** 坐标体系）"""
        self.size = -1
        """节点大小, 0表示隐藏, -1表示自动"""
        self.node_id = node_id
        self.type = 0
        """节点类型, 0表示无, 1表示Room, 2表示Inter, 3表示Cont, 4表示Item"""
        self.root_scene_id = root_scene

    def set_pos(self, x, y):
        self.pos = (x, y)

    def set_size(self, size):
        self.size = size

    def add_son_node(self, node_id):
        """
        添加一个子节点
        :param node_id: 所要添加的子节点的 node id
        :return: 0  -> 成功
                 -1 -> 已存在 node id 为 node_id 的子节点
                 -2 -> 不存在 node id 为 node_id 的子节点
                 -3 -> 当前 node 不支持添加子节点 (Inter Node 或 Item Node)
                 -4 -> 当前 node 不支持添加此类型的子节点 (Cont Node 只能添加 Item Node 的子节点)
                 -5 -> node id 为 node_id 的节点已有父节点
        """
        if node_id in self.son_node_ids:
            return -1
        if not Node.node_exist(node_id):
            return -2
        if self.is_inter() or self.is_item():
            return -3
        if self.is_cont() and not Node.get_node(node_id).is_item():
            return -4
        if Node.get_node(node_id).father_node_id == "":
            return -5
        self.son_node_ids.append(node_id)
        Node.get_node(node_id).father_node_id = self.node_id

    def set_father_node(self, node_id):
        """
        设置父节点
        :param node_id: 所设置父节点的 node id
        :return: 0  -> 成功
                 -6 -> 不存在 node id 为 node_id 的子节点
                 -1 ~ -5 -> add_son_node 报错，对应 add_son_node
        """
        if not Node.node_exist(node_id):
            return -6
        return Node.get_node(node_id).add_son_node(self.node_id)

    def get_type(self):
        return (Node, RoomNode, InterNode, ContNode, ItemNode)[self.type]

    def is_room(self):
        return self.type == 1

    def is_inter(self):
        return self.type == 2

    def is_cont(self):
        return self.type == 3

    def is_item(self):
        return self.type == 4

    @classmethod
    def get_node(cls, node_id):
        return cls._nodes[node_id]


class RoomNode(Node):
    """
    房间，对应为长方形
    """
    _room_nodes = {}

    def __init__(self, node_id, root_scene):
        super().__init__(node_id, root_scene)
        RoomNode._room_nodes[node_id] = self
        self.type = 1

    @classmethod
    def node_exist(cls, node_id):
        if (node_id not in cls._room_nodes.keys()) or (cls.get_node(node_id) is None):
            return False
        return True

    @classmethod
    def get_node(cls, node_id):
        return cls._room_nodes[node_id]


class InterNode(Node):
    """
    可交互对象，对应平行四边形
    """
    _inter_nodes = {}

    def __init__(self, node_id, root_scene):
        super().__init__(node_id, root_scene)
        InterNode._inter_nodes[node_id] = self
        self.type = 2

    @classmethod
    def node_exist(cls, node_id):
        if (node_id not in cls._inter_nodes.keys()) or (cls.get_node(node_id) is None):
            return False
        return True

    @classmethod
    def get_node(cls, node_id):
        return cls._inter_nodes[node_id]


class ContNode(Node):
    """
    容器，继承自可交互对象，对应椭圆
    """
    _cont_nodes = {}

    def __init__(self, node_id, root_scene):
        super().__init__(node_id, root_scene)
        ContNode._cont_nodes[node_id] = self
        self.type = 3

    @classmethod
    def node_exist(cls, node_id):
        if (node_id not in cls._cont_nodes.keys()) or (cls._cont_nodes[node_id] is None):
            return False
        return True

    @classmethod
    def get_node(cls, node_id):
        return cls._cont_nodes[node_id]


class ItemNode(Node):
    """
    物品（可拾取），对应为圆形
    """
    _item_nodes = {}

    def __init__(self, node_id, root_scene):
        super().__init__(node_id, root_scene)
        ItemNode._item_nodes[node_id] = self
        self.type = 4

    @classmethod
    def node_exist(cls, node_id):
        if (node_id not in cls._item_nodes.keys()) or (cls._item_nodes[node_id] is None):
            return False
        return True

    @classmethod
    def get_node(cls, node_id):
        return cls._item_nodes[node_id]


class Scene:  # TODO: 完成渲染 + 操作
    """
    场景类型
    """
    _scenes = {}

    def __init__(self, scene_id, size=(800, 600)):
        if scene_id in Scene._scenes.keys() and Scene._scenes[scene_id] is not None:
            raise ValueError(f'The scene id of {scene_id} already exist.')
        self.id = scene_id
        Scene._scenes[scene_id] = self
        self.pygame_display = pygame.Surface(size)
        self.nodes: list[str] = []
        """包含场景中 **root node** 的 node id"""

    def add_node(self, node_id):
        self.nodes.append(node_id)

    @classmethod
    def get_scene(cls, scene_id):
        return cls._scenes[scene_id]

    @classmethod
    def scene_exist(cls, scene_id):
        return scene_id in cls._scenes.keys() and cls.get_scene(scene_id) is not None


def register_node(root_scene_id: str, node_id: str, node_type, pos: tuple[float], father_node_id: str = "",
                  size: int = -1):
    """
    :param node_type: 0-4中的整数或Node(及继承自)类型
    :param size: 节点大小
    :param root_scene_id:
    :param node_id:
    :param father_node_id:
    :param pos: **几何中心** 的坐标
    :return: -1：root_scene_id 不存在对应的 Scene
             -2：node_id 已存在
             -3：father_node_id 设置失败
             -4：不合法的 node_type
    """
    if not Scene.scene_exist(root_scene_id):
        return -1
    if Node.node_exist(node_id):
        return -2
    node = None
    if node_type in (Node, RoomNode, InterNode, ContNode, ItemNode):
        node = node_type(node_id)
    elif node_type in range(5):
        node = (Node, RoomNode, InterNode, ContNode, ItemNode)[node_type](node_id)
    else:
        return -4
    node.set_size(size)
    node.set_pos(pos[0], pos[1])
    if father_node_id != '':
        if node.set_father_node(father_node_id):
            return -3


if __name__ == '__main__':  # TEST
    pygame.display.set_caption('MindMapGame Demo')
    screen = pygame.display.set_mode((800, 600))
    scene1 = Scene('scene1')
