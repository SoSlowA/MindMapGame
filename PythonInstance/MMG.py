from time import sleep

import pygame

pygame.init()

_FONT = './MCFONT.ttf'
_FONT_BASE_SIZE = 10

__backpack: list[str] = []
__hand: str = ''
__max_backpack_num = 4

# TODO: 关于 ITEM 和 NODE 的 DESCRIBE 系统
# TODO: 父子 NODE 之间的连接


def get_hand_id():
    return __hand


def set_hand_id(item_id):
    global __hand
    if not Item.item_exist(item_id):
        return -1
    __hand = item_id
    return 0


def is_in_back(item_id):
    return item_id in __backpack


def is_in_hand(item_id):
    return item_id == __hand


def set_back_item(item_id, ind):
    if not Item.item_exist(item_id):
        return -1
    if ind not in range(__max_backpack_num):
        return -2
    __backpack[ind] = item_id
    return 0


class Item:
    _items = {}

    @classmethod
    def item_exist(cls, item_id):
        if (item_id not in cls._items.keys()) or (cls.get_item(item_id) is None):
            return False
        return True

    @classmethod
    def get_item(cls, item_id):
        return cls._items[item_id]

    def __init__(self, item_id, name: str):
        if Item.item_exist(item_id):
            raise ValueError(f'The item id of {item_id} already exist.')
        self.item_id = item_id
        Item._items[item_id] = self
        self.name = name


class Node:
    _nodes = {}

    @classmethod
    def node_exist(cls, node_id):
        if (node_id not in cls._nodes.keys()) or (cls.get_node(node_id) is None):
            return False
        return True

    def __init__(self, node_id, root_scene: str, father_node_id: str = '', __dont_initialize_surface: bool = False):
        if Node.node_exist(node_id):
            raise ValueError(f'The node id of {node_id} already exist.')
        Node._nodes[node_id] = self
        self.father_node_id: str = father_node_id
        """节点的父节点的 node id, 空串表示没有父节点"""
        self.son_node_ids: list[str] = []
        self.pos = (None, None)
        """节点在 **平面直角坐标系** 的坐标（基于 **Pygame** 坐标体系，左上角）"""
        self.size = 1
        """节点大小，0 表示隐藏，-1 表示自动 (WIP)"""
        self.node_id = node_id
        self.type = 0
        """节点类型，0 表示无，1 表示 Room, 2 表示 Inter, 3 表示 Cont, 4 表示 Item"""
        self.set_father_node(father_node_id)
        self.root_scene_id = root_scene
        self.at_show: bool = False
        self.show_rules = []
        self.word: str = ''
        self.describe: str = ''
        self.pygame_surface_size = (80 * self.size, 60 * self.size)
        self.surface = None if __dont_initialize_surface else pygame.Surface(self.pygame_surface_size)
        self.pygame_word_font = pygame.font.SysFont('kaiti', _FONT_BASE_SIZE * 2 * self.size)
        self.pygame_font = pygame.font.SysFont('kaiti', _FONT_BASE_SIZE)
        self.command = None
        if not __dont_initialize_surface:
            self.surface.fill('white')
        if not self.father_node_id:
            Scene.get_scene(root_scene).add_node(node_id)

    def set_word(self, word: str):
        self.word = word

    def set_describe(self, describe: str):
        self.describe = describe

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
        if not node_id:
            if self.father_node_id:
                Node.get_node(self.father_node_id).remove_son(node_id)
            else:
                return 0
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

    def show(self):
        if not self.father_node_id or Node.get_node(self.father_node_id).is_shown():  # 如果父节点没有显示，则子节点不显示
            self.at_show = True

    def hide(self):
        self.at_show = False

    def is_shown(self):
        return self.at_show

    def rule_show(self):
        for rule in self.show_rules:
            if not rule:
                return -1
        self.show()
        return 0

    def son_show(self):
        for son in self.son_node_ids:
            Node.get_node(son).rule_show()

    def pygame_surface_update(self) -> pygame.Surface:
        pass

    def get_sons(self):
        return self.son_node_ids

    def get_shown_sons(self):
        __re = []
        for nid in self.son_node_ids:
            if Node.get_node(nid).is_shown():
                __re.append(nid)
        return __re

    def remove(self):
        self.hide()
        Node.get_node(self.father_node_id).remove_son(self.node_id)

    def remove_son(self, node_id):
        if node_id not in self.son_node_ids:
            return -1  # 没有这个子节点
        self.son_node_ids.remove(node_id)
        Node.get_node(node_id).father_node_id = ''


class RoomNode(Node):
    """
    房间，对应为长方形
    """
    _room_nodes = {}

    def __init__(self, node_id, root_scene, father_node_id: str = ''):
        super().__init__(node_id, root_scene, father_node_id)
        RoomNode._room_nodes[node_id] = self
        self.type = 1
        self.command = self.son_show
        self.opened: bool = False

    @classmethod
    def node_exist(cls, node_id):
        if (node_id not in cls._room_nodes.keys()) or (cls.get_node(node_id) is None):
            return False
        return True

    @classmethod
    def get_node(cls, node_id):
        return cls._room_nodes[node_id]

    def pygame_surface_update(self) -> pygame.Surface:
        surface = self.surface
        surface.fill('white')
        pygame.draw.rect(surface, 'black', (0, 0, 80 * self.size, 60 * self.size), 3, self.size * 5)
        word = self.pygame_word_font.render(self.word, True, 'black')
        surface.blit(word, (40 * self.size - word.get_size()[0] * 0.5, 30 * self.size - word.get_size()[1] * 0.5))
        return surface

    def rule_show(self):
        for rule in self.show_rules:
            if not rule:
                return -1
        self.show()
        if self.opened:
            self.son_show()


class InterNode(Node):
    """
    可交互对象，对应平行四边形
    """
    _inter_nodes = {}

    def __init__(self, node_id, root_scene, father_node_id: str = ''):
        super().__init__(node_id, root_scene, father_node_id)
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

    def pygame_surface_update(self) -> pygame.Surface:
        surface = self.surface
        surface.fill('white')
        pygame.draw.polygon(
            surface,
            'black',
            ((10 * self.size, 0), (80 * self.size, 0), (70 * self.size, 60 * self.size), (0, 60 * self.size)),
            3
        )
        word = self.pygame_word_font.render(self.word, True, 'black')
        surface.blit(word, (40 * self.size - word.get_size()[0] * 0.5, 30 * self.size - word.get_size()[1] * 0.5))
        return surface


class ContNode(InterNode):
    """
    容器，继承自可交互对象，对应椭圆
    """
    _cont_nodes = {}

    def __init__(self, node_id, root_scene, father_node_id: str = ''):
        super().__init__(node_id, root_scene, father_node_id)
        ContNode._cont_nodes[node_id] = self
        self.type = 3
        self.command = self.son_show

    @classmethod
    def node_exist(cls, node_id):
        if (node_id not in cls._cont_nodes.keys()) or (cls._cont_nodes[node_id] is None):
            return False
        return True

    @classmethod
    def get_node(cls, node_id):
        return cls._cont_nodes[node_id]

    def pygame_surface_update(self) -> pygame.Surface:
        surface = self.surface
        surface.fill('white')
        pygame.draw.rect(surface, 'black', (0, 0, 80 * self.size, 60 * self.size), 3, self.size * 30)
        word = self.pygame_word_font.render(self.word, True, 'black')
        surface.blit(word, (40 * self.size - word.get_size()[0] * 0.5, 30 * self.size - word.get_size()[1] * 0.5))
        return surface


class ItemNode(Node):
    """
    物品（可拾取），对应为圆形
    """
    _item_nodes = {}

    def __init__(self, node_id, root_scene, father_node_id: str = '', item_id: str = ''):
        super().__init__(node_id, root_scene, father_node_id, True)
        ItemNode._item_nodes[node_id] = self
        self.type = 4
        self.pygame_surface_size = (60 * self.size, 60 * self.size)
        self.surface = pygame.Surface(self.pygame_surface_size)
        self.item_id = item_id

    def set_item(self, item_id: str):
        self.item_id = item_id

    @classmethod
    def node_exist(cls, node_id):
        if (node_id not in cls._item_nodes.keys()) or (cls._item_nodes[node_id] is None):
            return False
        return True

    @classmethod
    def get_node(cls, node_id):
        return cls._item_nodes[node_id]

    def pygame_surface_update(self) -> pygame.Surface:
        surface = self.surface
        surface.fill('white')
        pygame.draw.circle(surface, 'black', (30 * self.size, 30 * self.size), 30, 3)
        word = self.pygame_word_font.render(self.word, True, 'black')
        surface.blit(word, (30 * self.size - word.get_size()[0] * 0.5, 30 * self.size - word.get_size()[1] * 0.5))
        return surface

    def pick_up(self):
        if get_hand_id():
            return -1  # 手上已经有了东西
        set_hand_id(self.item_id)
        return 0


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

    def display_update(self):
        self.pygame_display.fill('white')
        for _node in self.nodes:
            current_node = Node.get_node(_node)
            current_node.rule_show()
            if current_node.is_shown():
                current_node.pygame_surface_update()
                self.pygame_display.blit(current_node.surface, current_node.pos)


def create_node(root_scene_id: str, node_id: str, node_type, pos: tuple[float, float], father_node_id: str = "",
                size: int = 1):
    """
    :param node_type: 0-4 中的整数或 Node(及继承自) 类型
    :param size: 节点大小
    :param root_scene_id:
    :param node_id:
    :param father_node_id:
    :param pos: **几何中心** 的坐标
    :return: -1：root_scene_id 不存在对应的 Scene
             -2：node_id 已存在
             -3：father_node_id 设置失败
             -4：不合法的 node_type
             -5：scene 中已存在该根节点
             Node Object：建立的 NODE
    """
    if not Scene.scene_exist(root_scene_id):
        return -1
    if Node.node_exist(node_id):
        return -2
    _node = None
    if node_id in Scene.get_scene(root_scene_id).nodes:
        return -5
    if node_type in (Node, RoomNode, InterNode, ContNode, ItemNode):
        _node = node_type(node_id, root_scene_id)
    elif node_type in range(5):
        _node = (Node, RoomNode, InterNode, ContNode, ItemNode)[node_type](node_id, root_scene_id)
    else:
        return -4
    _node.set_size(size)
    _node.set_pos(pos[0], pos[1])
    if father_node_id != '':
        if _node.set_father_node(father_node_id):
            return -3
    return _node


class Rule:
    _rules = {}

    def __init__(self, rule_id):
        if Rule.rule_exist(rule_id):
            raise ValueError(f'The rule id of {rule_id} already exist.')
        self.type = 0
        """0 -> 默认\n1 -> 比较\n2 -> 逻辑运算\n3 -> 背包/手上 Item 判断"""
        self.rule_id = rule_id
        Rule._rules[rule_id] = self

    def judge(self):
        return False

    @classmethod
    def rule_exist(cls, rule_id):
        return rule_id in cls._rules.keys() and cls._rules[rule_id] is not None

    @classmethod
    def get_rule(cls, rule_id):
        return cls._rules[rule_id]

    def __bool__(self):
        return self.judge()


class RuleCompare(Rule):
    _c_rules = {}

    def __init__(self, rule_id, c_type, a, b):
        """
        :param rule_id:
        :param c_type: 1 -> 大于 2 -> 小于 取与表或（0 -> 相等，1 -> 大于，2 -> 小于，3 -> 不等于）
        :param a: 一项，为常量或函数变量
        :param b: 二项，为常量或函数变量
        """
        super().__init__(rule_id)
        self.type = 1
        RuleCompare._c_rules[rule_id] = self
        self.c_type = c_type
        self.a = a
        self.b = b

    def judge(self):
        is_g = self.c_type & 1
        is_l = self.c_type & 2
        return is_g * (self.a > self.b) or is_l * (self.a < self.b)

    @classmethod
    def rule_exist(cls, rule_id):
        return rule_id in cls._c_rules.keys() and cls._rules[rule_id] is not None

    @classmethod
    def get_rule(cls, rule_id):
        return cls._c_rules[rule_id]


class RuleLogic(Rule):
    _l_rules = {}

    def __init__(self, rule_id, c_type, rule_id_a, rule_id_b):
        super().__init__(rule_id)
        self.type = 2
        self.id_a = rule_id_a
        self.id_b = rule_id_b
        RuleLogic._l_rules[rule_id] = self
        self.c_type = c_type
        """1-> 与，2-> 或，3-> 异或，4-> 非（此时，rule_id_b 取 None）"""

    def judge(self):
        if self.c_type == 1:
            return Rule.get_rule(self.id_a).judge() and Rule.get_rule(self.id_b)
        if self.c_type == 2:
            return Rule.get_rule(self.id_a).judge() or Rule.get_rule(self.id_b)
        if self.c_type == 3:
            return Rule.get_rule(self.id_a).judge() ^ Rule.get_rule(self.id_b)
        if self.c_type == 4:
            return not Rule.get_rule(self.id_a).judge()
        return False

    @classmethod
    def rule_exist(cls, rule_id):
        return rule_id in cls._l_rules.keys() and cls._l_rules[rule_id] is not None

    @classmethod
    def get_rule(cls, rule_id):
        return cls._l_rules[rule_id]


class RuleItem(Rule):
    _i_rules = {}

    def __init__(self, rule_id, b_type, item_id):
        super().__init__(rule_id)
        self.type = 3
        RuleItem._i_rules[rule_id] = self
        self.b_type = b_type
        """1-> 在手上？，2-> 在背包里 (含手)？，3-> 在背包里 (不含手)？"""
        self.item_id = item_id

    def judge(self):
        if self.b_type == 1:
            return is_in_hand(self.item_id)
        if self.b_type == 2:
            return is_in_hand(self.item_id) or is_in_back(self.item_id)
        if self.b_type == 3:
            return is_in_back(self.item_id)
        return False

    @classmethod
    def rule_exist(cls, rule_id):
        return rule_id in cls._i_rules.keys() and cls._i_rules[rule_id] is not None

    @classmethod
    def get_rule(cls, rule_id):
        return cls._i_rules[rule_id]


# TODO: 按键 HOOK


if __name__ == '__main__':  # TEST
    pygame.display.set_caption('MindMapGame Demo')
    screen = pygame.display.set_mode((800, 600))
    scene1 = Scene('scene1')
    node_r = create_node('scene1', 'node2', RoomNode, (100.0, 100.0))
    node = ItemNode('node1', 'scene1', )
    node.set_pos(10.0, 100.0)
    node.set_word('阿爸')
    while True:
        scene1.display_update()
        screen.blit(scene1.pygame_display, (0, 0))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        sleep(1 / 20)
