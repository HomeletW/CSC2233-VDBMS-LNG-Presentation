from manim import *
import random
import math
from typing import List, Dict, Tuple, Any

random.seed(1028)

SOLID = "solid"
DASHED = "dashed"


class NodeBase:
    def get_node(self, name):
        raise NotImplementedError


class EdgeManager:
    def __init__(self, *nodes_and_graphs):
        self.edge_map: Dict[Tuple[str, str], Any] = {}
        self.edge_highlight_state_map: Dict[Tuple[str, str], Any] = {}
        self.node_highlight_state_map: Dict[str, Any] = {}
        self.nodes = []
        queue = list(nodes_and_graphs)
        while len(queue) != 0:
            node = queue.pop()
            if issubclass(type(node), NodeBase):
                self.nodes.append(node)
            elif isinstance(node, VGroup):
                queue.extend(list(node))

    @staticmethod
    def create_arrow_from_points(from_pos, to_pos, connect_bot_to_top=False, connect_top_to_bot=False,
                                 pos_buff=.5, style=SOLID, bidirectional=False, color=BLUE, stroke_width=4,
                                 tip_width=.25, buff=.5):
        if style == DASHED:
            arrow = (DashedLine(from_pos, to_pos,
                                color=color, stroke_width=stroke_width, buff=buff, dash_length=.25)
                     .add_tip(tip_width=tip_width, tip_length=tip_width))
        elif style == SOLID:
            if bidirectional:
                arrow = DoubleArrow(from_pos, to_pos, color=color, stroke_width=stroke_width,
                                    buff=buff, tip_length=tip_width, max_tip_length_to_length_ratio=100)
            else:
                arrow = Arrow(from_pos, to_pos, color=color, stroke_width=stroke_width,
                              buff=buff, tip_length=tip_width,
                              max_tip_length_to_length_ratio=100)
        else:
            raise Exception(f"Invalid style {style}")
        return arrow

    @staticmethod
    def create_arrow(from_obj, to_obj, connect_bot_to_top=False, connect_top_to_bot=False, pos_buff=.5,
                     style=SOLID, bidirectional=False, color=BLUE, stroke_width=4, tip_width=.25, buff=.5):
        if connect_bot_to_top:
            from_pos, to_pos = from_obj.get_bottom() + DOWN * pos_buff, to_obj.get_top() + UP * pos_buff
        elif connect_top_to_bot:
            from_pos, to_pos = from_obj.get_top() + UP * pos_buff, to_obj.get_bottom() + DOWN * pos_buff
        else:
            from_pos, to_pos = from_obj.get_center(), to_obj.get_center()
        return EdgeManager.create_arrow_from_points(
            from_pos, to_pos, connect_bot_to_top=connect_bot_to_top, connect_top_to_bot=connect_top_to_bot,
            pos_buff=pos_buff, style=style, bidirectional=bidirectional, color=color, stroke_width=stroke_width,
            tip_width=tip_width, buff=buff)

    def _find_obj(self, name):
        for n_or_g in self.nodes:
            node = n_or_g.get_node(name)
            if node is not None:
                return node
        raise Exception(f"Could not find {name}")

    def _find_obj_with_index(self, name):
        for i, n_or_g in enumerate(self.nodes):
            node = n_or_g.get_node(name)
            if node is not None:
                return i, node
        raise Exception(f"Could not find {name}")

    def _find_edge(self, key):
        f, t = key
        result = self.edge_map.get((f, t), None)
        if result is not None:
            return result
        return self.edge_map[(t, f)]

    def add_edges(self, *keys, **arrow_kwargs):
        if len(keys) == 0:
            return []
        arrows = [self.create_arrow(self._find_obj(from_obj_name), self._find_obj(to_obj_name), **arrow_kwargs)
                  for (from_obj_name, to_obj_name) in keys]
        for (f, t), arrow in zip(keys, arrows):
            self.edge_map[(f, t)] = arrow
        return arrows

    def remove_edges(self, *keys):
        for (f, t) in keys:
            del self.edge_map[(f, t)]

    def get_objects(self, *names, all=False, inverse=False):
        if all:
            return self.nodes
        if inverse:
            return (obj for obj in self.nodes if not any(obj.get_node(n) is not None for n in names))
        return (self._find_obj(name) for name in names)

    def get_objects_with_index(self, *names, all=False, inverse=False):
        if all:
            return enumerate(self.nodes)
        if inverse:
            return ((i, obj)
                    for i, obj in enumerate(self.nodes)
                    if not any(obj.get_node(n) is not None for n in names))
        return (self._find_obj_with_index(name) for name in names)

    def get_edges(self, *keys, all=False, inverse=False):
        if all:
            return self.edge_map.values()
        if inverse:
            key_sets = set(keys)
            key_sets.union(set((t, f) for f, t in keys))  # reverse edges
            return (value for key, value in self.edge_map.items() if key not in key_sets)
        return (self._find_edge(key) for key in keys)

    def get_edges_with_keys(self, *keys, all=False, inverse=False):
        if all:
            return self.edge_map.items()
        if inverse:
            key_sets = set(keys)
            key_sets.union(set((t, f) for f, t in keys))
            return ((key, value) for key, value in self.edge_map.items() if key not in key_sets)
        return ((key, self._find_edge(key)) for key in keys)

    def create_edges(self, *keys, **kwargs):
        return (Create(arrow) for arrow in self.get_edges(*keys, **kwargs))

    def grow_edges(self, *keys, **kwargs):
        return (GrowArrow(arrow) for arrow in self.get_edges(*keys, **kwargs))

    def fadeIn_edges(self, *keys, **kwargs):
        return (FadeIn(arrow) for arrow in self.get_edges(*keys, **kwargs))

    def fadeOut_edges(self, *keys, **kwargs):
        return (FadeOut(arrow) for arrow in self.get_edges(*keys, **kwargs))

    def passing_edges(self, *keys, time_width=.5, **kwargs):
        return (ShowPassingFlash(arrow, time_width=time_width) for arrow in self.get_edges(*keys, **kwargs))

    def flash_edges(self, *keys, **kwargs):
        return (Flash(arrow) for arrow in self.get_edges(*keys, **kwargs))

    def indicate_edges(self, *keys, **kwargs):
        return (Indicate(arrow) for arrow in self.get_edges(*keys, **kwargs))

    def wave_edges(self, *keys, **kwargs):
        return (ApplyWave(arrow, amplitude=0.5) for arrow in self.get_edges(*keys, **kwargs))

    def fadeIn_nodes(self, *names, **kwargs):
        return (FadeIn(obj) for obj in self.get_objects(*names, **kwargs))

    def fadeOut_nodes(self, *names, **kwargs):
        return (FadeOut(obj) for obj in self.get_objects(*names, **kwargs))

    def circumscribe_nodes(self, *names, time_width=.5, **kwargs):
        return (Circumscribe(obj, time_width=time_width) for obj in self.get_objects(*names, **kwargs))

    def highlight_edges(self, *keys):
        animations = []
        for k, arrow in self.get_edges_with_keys(*keys, inverse=True):
            self.edge_highlight_state_map[k] = 1
            animations.append(arrow.animate.set_opacity(.1))
        return animations

    def add_highlight_edges(self, *keys):
        animations = []
        for k, arrow in self.get_edges_with_keys(*keys):
            assert k in self.edge_highlight_state_map
            org_opa = self.edge_highlight_state_map[k]
            del self.edge_highlight_state_map[k]
            animations.append(arrow.animate.set_opacity(org_opa))
        return animations

    def undo_highlight_edges(self, *keys):
        animations = []
        for k, arrow in self.get_edges_with_keys(*keys, inverse=True):
            org_opa = self.edge_highlight_state_map[k]
            del self.edge_highlight_state_map[k]
            animations.append(arrow.animate.set_opacity(org_opa))
        return animations

    def cleanup_highlight_edges(self, *keys):
        for k, arrow in self.get_edges_with_keys(*keys, inverse=True):
            del self.edge_highlight_state_map[k]

    def highlight_nodes(self, *names):
        animations = []
        for k, obj in self.get_objects_with_index(*names, inverse=True):
            self.node_highlight_state_map[k] = obj.copy()
            animations.append(obj.animate.set_opacity(.1))
        return animations

    def add_highlight_nodes(self, *names):
        animations = []
        for k, obj in self.get_objects_with_index(*names):
            assert k in self.node_highlight_state_map
            org_obj = self.node_highlight_state_map[k]
            del self.node_highlight_state_map[k]
            animations.append(Transform(obj, org_obj))
        return animations

    def undo_highlight_nodes(self, *names):
        animations = []
        for k, obj in self.get_objects_with_index(*names, inverse=True):
            org_obj = self.node_highlight_state_map[k]
            del self.node_highlight_state_map[k]
            animations.append(Transform(obj, org_obj))
        return animations

    def cleanup_highlight_nodes(self, *names):
        for k, obj in self.get_objects_with_index(*names, inverse=True):
            del self.node_highlight_state_map[k]


class LabelNode(VGroup, NodeBase):
    def __init__(self, title, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.title = title.copy()
        self.add(self.title)

    def get_node(self, name):
        if name == self.name:
            return self
        else:
            return None


class NodeGraph(VGroup, NodeBase):
    def __init__(self, name, title, node_params: List[Dict], box_size: Tuple[float, float],
                 title_padding=1.3, box_padding=.5, bot_padding=.5, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.box_width, self.box_height = box_size
        self.box_padding = box_padding
        self.title_padding = title_padding
        self.bot_padding = bot_padding
        self.node_params = node_params
        self.box = (RoundedRectangle(corner_radius=box_padding, height=self.box_height, width=self.box_width)
                    .set_stroke(color=WHITE, width=2).set_fill(opacity=0))
        self.title = title.copy().next_to(self.box.get_top(),
                                          DOWN * (title_padding / 2),
                                          aligned_edge=UP)
        node_locations = self._generate_uniform_locations()
        self.nodes = [self.make_graph_nodes(**param).move_to(self.box.get_corner(UL) + RIGHT * loc_x + DOWN * loc_y)
                      for param, (loc_x, loc_y) in zip(node_params, node_locations)]
        self.node_names = [param["rep_name"] for param in self.node_params]
        self.node_map = {param["rep_name"]: idx + 2 for idx, param in enumerate(self.node_params)}
        self.add(self.title, self.box, *self.nodes)

    def get_node(self, name):
        if name == self.name:
            return self
        idx = self.node_map.get(name, None)
        if idx is not None:
            return self[idx]
        return None

    def fadeOut_box(self):
        return (FadeOut(self.box, self.title),)

    def fadeIn_box(self):
        return (FadeIn(self.box, self.title),)

    def fadeOut_nodes(self, *names, all=False):
        if all:
            return (FadeOut(node) for node in self.nodes)
        return (FadeOut(self.get_node(name)) for name in names)

    def fadeIn_nodes(self, *names, all=False):
        if all:
            return (FadeIn(node) for node in self.nodes)
        return (FadeIn(self.get_node(name)) for name in names)

    def fully_connect_nodes(self, edge_manger: EdgeManager):
        keys = [(self.node_names[i], self.node_names[j])
                for i in range(len(self.nodes)) for j in range(i + 1, len(self.nodes))]
        arrows = edge_manger.add_edges(*keys, bidirectional=True, stroke_width=2, buff=0, tip_width=.125)
        self.add(*arrows)

    def _generate_uniform_locations(self):
        """
        Generate a list of unique (x, y) locations ensuring no overlap and a minimum distance between points,
        distributed evenly around a central point with some randomness, while ensuring they stay within a given bounding box.
        """
        top_padding = max(self.box_padding, self.title_padding)
        bot_padding = max(self.box_padding, self.bot_padding)
        num_points = len(self.node_params)
        center = (self.box_width / 2, self.box_height / 2)
        angle_per_item = 2 * math.pi / (num_points + 1)
        delta_angle_per_item = angle_per_item / num_points / 2
        x_range = (self.box_padding, self.box_width - self.box_padding)
        y_range = (top_padding, self.box_height - bot_padding)
        angle_delta_range = (-delta_angle_per_item / 2, delta_angle_per_item / 2)
        radius = (min((x_range[1] - x_range[0]), (y_range[1] - y_range[0]))) / 2
        radius_range = (radius / 4 * 3, radius / 4 * 6)
        min_distance = max(param.get("radius", .3) * 3 for param in self.node_params)

        attempts = 0
        max_attempts = num_points * 100

        locations = []
        while len(locations) < num_points and attempts < max_attempts:
            curr_angle = len(locations) * angle_per_item + random.uniform(*angle_delta_range)
            curr_radius = random.uniform(*radius_range)
            x = center[0] + curr_radius * math.cos(curr_angle)
            y = center[1] + curr_radius * math.sin(curr_angle)

            # Ensure the point stays within the bounding box
            if x_range[0] <= x <= x_range[1] and y_range[0] <= y <= y_range[1]:
                if all(math.dist((x, y), existing) >= min_distance for existing in locations):
                    locations.append((x, y))
            attempts += 1

        if len(locations) < num_points:
            raise Exception("Warning: Could not generate the required number of points with given constraints.")

        random.shuffle(locations)
        return locations

    @staticmethod
    def make_graph_nodes(name, radius=.5, font_size=56, **kwargs):
        c = Circle(radius=radius).set_stroke(color=WHITE, width=2).set_fill(opacity=0)
        t = Tex(name, font_size=font_size).move_to(c.get_center())
        return VGroup(c, t)
