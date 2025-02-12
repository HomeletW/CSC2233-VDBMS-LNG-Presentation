from __future__ import annotations

from manim import *
from manim_slides.slide import Slide

config.frame_width = 30 * 1.5
config.frame_height = 15 * 1.5

from graph_util import LabelNode, NodeGraph, EdgeManager, SOLID, DASHED


def TransformTo(from_obj, to_obj):
    return TransformFromCopy(from_obj, to_obj), FadeOut(from_obj)


document_icon = SVGMobject("document-add-svgrepo-com.svg", fill_color=WHITE, fill_opacity=1)
embedding_icon = SVGMobject("graph-infographic-data-matrix-element-svgrepo-com.svg", fill_color=WHITE, fill_opacity=1)


def make_brace_with_label(obj, text, use_tex=False, font_size=48, text_buff=0., **brace_kwargs):
    b = Brace(obj, **brace_kwargs)
    if use_tex:
        t = b.get_tex(text, buff=text_buff)
    else:
        t = b.get_text(text, buff=text_buff)
    t.set_font_size(font_size)
    return VGroup(b, t)


def make_multiline_text(*texts, use_tex=True, font_size=72., buff: list | float = .5):
    buff_value = buff if isinstance(buff, list) else [buff] * (len(texts) - 1)
    lines = []
    last_line = None
    for i, text in enumerate(texts):
        if use_tex:
            t = Tex(text, font_size=font_size)
        else:
            t = Text(text, font_size=font_size)
        if last_line is not None:
            t.next_to(last_line, DOWN, buff=buff_value[i - 1], aligned_edge=LEFT)
        last_line = t
        lines.append(t)
    return VGroup(*lines)


def make_label_rep(name, color, font_size=48, buff=.1):
    t = Text(name, font_size=font_size, color=color)
    r = SurroundingRectangle(t, buff=buff).set_stroke(color=color, width=3).set_fill(opacity=0)
    return VGroup(t, r)


def make_label_set_rep(label_set, font_size=60, gap_left=.25, gap_right=.25, gap=.5):
    reps = [Text("{", font_size=font_size), *[label.copy() for label in label_set], Text("}", font_size=font_size)]
    last_rep = None
    for i, rep in enumerate(reps):
        if last_rep is not None:
            if i == 1:
                rep.next_to(last_rep, RIGHT, buff=gap_left)
            elif i == len(reps) - 1:
                rep.next_to(last_rep, RIGHT, buff=gap_right)
            else:
                rep.next_to(last_rep, RIGHT, buff=gap)
        last_rep = rep
    return VGroup(*reps)


def make_legend(*arrow_configs, font_size=54, buff=.25, arrow_length=2.):
    legend = VGroup()
    for arrow_config in arrow_configs:
        t = Text(arrow_config["name"], font_size=font_size)
        a = EdgeManager.create_arrow_from_points(ORIGIN, ORIGIN + RIGHT * arrow_length,
                                                 **arrow_config["arrow_param"])
        g = VGroup(a, t)
        g.arrange(RIGHT, buff=buff)
        legend.add(g)
    legend.arrange(DOWN, buff=buff, aligned_edge=LEFT)
    rect = SurroundingRectangle(legend, buff=buff, color=WHITE, stroke_width=4)
    legend.add(rect)
    return legend


def make_document_rep(attribute_dict, icon_template=None, show_text=False, padding=.5, corner_cut=.7):
    if icon_template is not None:
        icon = icon_template.copy()
    else:
        icon = NodeGraph.make_graph_nodes(attribute_dict["name"], font_size=100, radius=.8)
    if show_text:
        attribute = Text(attribute_dict["label_set"]["full_name"], font_size=48)
    else:
        attribute = VGroup(*[rep.copy() for rep in attribute_dict["label_set"]["label_reps"]])
        attribute.arrange_in_grid(rows=len(attribute_dict["label_set"]["label_reps"]), cols=1, buff=.3)
    icon.move_to(ORIGIN)
    attribute.move_to(ORIGIN + RIGHT * (icon.width / 2 + padding + attribute.width / 2))
    width = max(icon.width + attribute.width + 3 * padding, 4.9865234)
    height = max(icon.height, attribute.height) + 2 * padding
    paper = Polygon(
        [-width / 2, -height / 2, 0],  # Bottom-left
        [width / 2, -height / 2, 0],  # Bottom-right
        [width / 2, height / 2, 0],  # Top-right
        [-width / 2 + corner_cut, height / 2, 0],  # Cut-off point (adjust for bigger/smaller cut)
        [-width / 2, height / 2 - corner_cut, 0],  # Slant corner cut
        [-width / 2, -height / 2, 0],  # Closing point
    ).set_stroke(color=WHITE, width=5).set_fill(color=BLACK, opacity=1)
    paper.align_to(icon, LEFT).shift(LEFT * padding)
    return VGroup(paper, icon, attribute).move_to(ORIGIN)


def filter_edges(edges, f=None, t=None, inverse=False):
    if not inverse:
        if f is None and t is None:
            return edges
        elif f is None:
            t_set = set(t)
            return (e for e in edges if e[1] in t_set)
        elif t is None:
            f_set = set(f)
            return (e for e in edges if e[0] in f_set)
        else:
            t_set = set(t)
            f_set = set(f)
            return (e for e in edges if e[0] in f_set and e[1] in t_set)
    else:
        materialized_edges = list(edges)
        filtered_edges = set(*filter_edges(materialized_edges, f=f, t=t, inverse=False))
        return [e for e in materialized_edges if e not in filtered_edges]


class LNGDemonstration(Slide):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attribute_key_color_map = {"venue": RED, "year": BLUE, "subject": GREEN, "with code": ORANGE}
        self.labels = [("venue", "SIGMOD"),
                       ("year", "2024"),
                       ("subject", "graph"),
                       ("year", "2025"),
                       ("subject", "DBMS"),
                       ("with code", "yes"),
                       ("venue", "VLDB"),
                       ("subject", "DG")]
        self.label_short_name = ["with_code" if k == "with code" else v for k, v, in self.labels]
        self.label_rep = [
            make_label_rep(short_name, self.attribute_key_color_map[k])
            for (k, v), short_name in zip(self.labels, self.label_short_name)
        ]
        self.label_sets_info = [
            {"labels": [1, 2, 3], "documents": [1, 21, 22], "entry": 1},
            {"labels": [1, 4, 5], "documents": [2, 11, 12], "entry": 11},
            {"labels": [1, 4, 5, 6], "documents": [3, 17, 18], "entry": 3},
            {"labels": [7, 2, 8], "documents": [4, 16], "entry": 16},
            {"labels": [1], "documents": [5, 6, 7], "entry": 5},
            {"labels": [1, 3], "documents": [13, 14, 15], "entry": 14},
            {"labels": [2], "documents": [8, 9, 10], "entry": 8},
            {"labels": [1, 4, 3, 6], "documents": [19, 20], "entry": 19},
        ]
        self.lng_edge_infos = [(5, 2), (5, 6), (7, 4), (7, 1), (2, 3), (6, 8), (6, 1)]
        self.ung_cross_group_edge_infos = [(5, 2), (5, 13), (7, 11), (6, 11),
                                           (2, 18), (12, 3), (11, 3),
                                           (14, 19), (13, 20), (15, 19), (15, 22),
                                           (9, 22), (10, 4), (8, 4)]
        self.ung_inner_graph_edge_infos = [(7, 6), (6, 7), (6, 5), (5, 7),
                                           (12, 2), (11, 12), (11, 2),
                                           (13, 14), (14, 13), (14, 15), (15, 14),
                                           (18, 17), (18, 3), (3, 18), (3, 17),
                                           (19, 20), (20, 19),
                                           (8, 9), (8, 10),
                                           (16, 4),
                                           (22, 21), (21, 22), (22, 1), (1, 22), (21, 1), (1, 21)]
        self.label_set_reps = [
            make_label_set_rep([self.label_rep[l_id - 1] for l_id in dic["labels"]])
            for ls_id, dic in enumerate(self.label_sets_info)
        ]
        self.label_sets = {
            ls_id + 1: {"id": ls_id + 1,
                        "labels": [self.labels[l_id - 1] for l_id in dic["labels"]],
                        "label_reps": [self.label_rep[l_id - 1] for l_id in dic["labels"]],
                        "label_set_rep": label_set_rep,
                        "rep_name": f"f{ls_id + 1}",
                        "full_name": "{" + ",\n".join(
                            ["{}={}".format(*self.labels[i - 1]) for i in dic["labels"]]) + "}",
                        "short_name": "{" + ",".join(
                            [self.label_short_name[l_id - 1] for l_id in dic["labels"]]) + "}",
                        "nodes": [],
                        "entry_vector": dic["entry"]}
            for ls_id, (dic, label_set_rep) in enumerate(zip(self.label_sets_info, self.label_set_reps))
        }
        self.documents = {
            d_id: {"id": d_id,
                   "rep_name": f"v{d_id}",
                   "name": f"$v_{{{d_id}}}$",
                   "label_set": self.label_sets[ls_id + 1]}
            for ls_id, dic in enumerate(self.label_sets_info)
            for d_id in dic["documents"]
        }
        self.document_to_label_set = {
            dic["rep_name"]: dic["label_set"]["rep_name"]
            for d_id, dic in self.documents.items()
        }
        for ls_id in self.label_sets:
            dic = self.label_sets_info[ls_id - 1]
            self.label_sets[ls_id]["nodes"] = [self.documents[d_id] for d_id in dic["documents"]]
        self.lng_edges = [(self.label_sets[f]["rep_name"], self.label_sets[t]["rep_name"])
                          for f, t in self.lng_edge_infos]
        self.ung_cross_group_edges = [(self.documents[f]["rep_name"], self.documents[t]["rep_name"])
                                      for f, t in self.ung_cross_group_edge_infos]
        self.ung_inner_graph_edges = [(self.documents[f]["rep_name"], self.documents[t]["rep_name"])
                                      for f, t in self.ung_inner_graph_edge_infos]
        self.legend_configs = [
            {"name": "Minimum Superset Relationship",
             "arrow_param": {"connect_top_to_bot": True, "pos_buff": .25, "buff": 0, "stroke_width": 8, "tip_width": .5,
                             "color": GREEN}},
            {"name": "LNG Edge",
             "arrow_param": {"connect_bot_to_top": True, "pos_buff": .25, "buff": 0, "stroke_width": 8, "tip_width": .5,
                             "color": ORANGE}},
            {"name": "UNG Inner Edge",
             "arrow_param": {"color": BLUE, "buff": 0, "stroke_width": 8, "tip_width": .5, }},
            {"name": "UNG Cross-Group Edge",
             "arrow_param": {"style": DASHED, "color": ORANGE, "buff": 0, "stroke_width": 8, "tip_width": .5, }},
            {"name": "LNG Edge (Overlaid on UNG)",
             "arrow_param": {"connect_bot_to_top": True, "pos_buff": .25, "buff": 0, "stroke_width": 8, "tip_width": .5,
                             "color": ORANGE}},
        ]
        self.title = None
        self.cross_group_edges_description_line_1_flag = False
        self.cross_group_edges_description_line_2_flag = False

    def _set_title(self, new_text):
        new_title = Tex(new_text, font_size=115).to_edge(UP)
        if self.title is None:
            self.title = new_title
            return FadeIn(self.title)
        else:
            return Transform(self.title, new_title)

    def _set_title_as_object(self, obj):
        new_title = obj.copy().to_edge(UP)
        if self.title is None:
            return Transform(obj, new_title)
        else:
            old_title = self.title
            return FadeOut(old_title), Transform(obj, new_title)

    def _set_title_as_new_object(self, obj):
        new_title = obj.to_edge(UP)
        if self.title is None:
            return FadeIn(new_title)
        else:
            old_title = self.title
            return FadeOut(old_title), FadeIn(new_title)

    def section_1(self):
        # show example document, and point to what is the "doc" and "attributes"
        self.next_slide(notes="Say we have an dataset, where each entry contains some unstructured data and a set of "
                              "associated structured attributes.\n\n"
                              "Here, we are seeing conference papers as examples.")
        example_document = make_document_rep(self.documents[1], icon_template=document_icon, show_text=True)
        print(example_document.width)
        self.play(FadeIn(example_document))
        self.next_slide(notes="We can generate an embedding vector for the unstructured data and do efficient NN "
                              "queries on them. But how do we combine the index for the vectors and the index for the "
                              "structured attributes.")
        example_document_new = make_document_rep(self.documents[1], icon_template=None, show_text=True)
        self.play(Transform(example_document, example_document_new))
        self.next_slide(notes="Now the paper's insight is to define an abstraction called label.")
        label_definition_example = VGroup(Text("venue", font_size=68),
                                          Text("=", font_size=68),
                                          Text("SIGMOD", font_size=68))
        label_definition_example.arrange(RIGHT, buff=1).move_to(ORIGIN + UP * 3)
        self.play(self._set_title("Define Label"),
                  example_document.animate.shift(DOWN * 3),
                  FadeIn(label_definition_example))
        self.next_slide(notes="Notice, each attribute has an attribute name and it's value assignment.")
        label_definition_example_attr_name = make_brace_with_label(label_definition_example[0],
                                                                   "Attr name",
                                                                   font_size=72, direction=UP, buff=.6,
                                                                   text_buff=.4)
        label_definition_example_value_assignment = make_brace_with_label(label_definition_example[2],
                                                                          "Value assignment",
                                                                          font_size=72, direction=UP, buff=.6,
                                                                          text_buff=.2)
        self.play(FadeIn(label_definition_example_attr_name, label_definition_example_value_assignment))
        self.next_slide(notes="Combined, we call each of such attribute assignment in the dataset an label.\n\n"
                              "And it's easy to show that there are finite numbers of labels in a dataset with only "
                              "discrete data types, "
                              "upper bounded by the length of the Cartesian Product between all attribute names and "
                              "all value assignments.")
        label_definition_example_rect = SurroundingRectangle(label_definition_example,
                                                             buff=.5)
        label_definition_example_text = Text("Label", font_size=72).next_to(label_definition_example_rect, RIGHT,
                                                                            buff=2)
        label_definition_example_arrow = Arrow(label_definition_example_text.get_left(),
                                               label_definition_example_rect.get_right())
        self.play(DrawBorderThenFill(label_definition_example_rect),
                  FadeIn(label_definition_example_arrow, label_definition_example_text))
        self.next_slide(notes="In this presentation, I am going to show a label as this colored rectangle thingy to "
                              "represent notation visually.\n\n"
                              "And if two labels has the same color, it means they have the same attribute name.\n\n"
                              "And if two labels has different color, it means they have the different attribute name.\n\n"
                              "The attribute value assignment is displayed in the center.")
        selected_label_definition_examples = [0, 6, 1]
        label_definition_example_column_1_rep = VGroup()
        label_definition_example_column_2_rep = VGroup()
        for selected_example in selected_label_definition_examples:
            txt_rep = Text("{} = {}".format(*self.labels[selected_example]), font_size=72)
            lb_rep = self.label_rep[selected_example].copy().scale(1.5)
            label_definition_example_column_1_rep.add(txt_rep)
            label_definition_example_column_2_rep.add(lb_rep)
        label_definition_example_column_1_rep.arrange(DOWN, buff=1.25, aligned_edge=ORIGIN)
        label_definition_example_column_2_rep.arrange(DOWN, buff=1, aligned_edge=ORIGIN)
        label_definition_example_rep = VGroup(label_definition_example_column_1_rep,
                                              label_definition_example_column_2_rep)
        label_definition_example_rep.arrange(RIGHT, buff=1, aligned_edge=ORIGIN).move_to(ORIGIN + UP * 3)
        self.play(
            FadeIn(label_definition_example_rep),
            FadeOut(label_definition_example, label_definition_example_rect, label_definition_example_attr_name,
                    label_definition_example_value_assignment, label_definition_example_arrow,
                    label_definition_example_text)
        )

        # label_definition_example_label_rep = self.label_rep[0].copy().scale(1.5)
        # label_definition_example_label_rep_group = VGroup(label_definition_example_label_rep)
        # label_definition_example_label_rep_group.move_to(ORIGIN + UP * 3)
        # self.play(FadeIn(label_definition_example_label_rep_group),
        #           FadeOut(label_definition_example, label_definition_example_rect, label_definition_example_attr_name,
        #                   label_definition_example_value_assignment, label_definition_example_arrow,
        #                   label_definition_example_text))
        # self.next_slide(notes="In this presentation, I am going to show a label as this colored rectangle thingy to "
        #                       "represent notation visually.")
        # label_definition_example_label_rep_2 = self.label_rep[6].copy().scale(1.5).next_to(
        #     label_definition_example_label_rep_group, RIGHT, buff=2)
        # label_definition_example_label_rep_group.add(label_definition_example_label_rep_2)
        # label_definition_example_label_rep_group_new = (label_definition_example_label_rep_group
        #                                                 .copy().arrange(RIGHT, buff=1))
        # label_definition_example_label_rep_group_new.move_to(ORIGIN + UP * 3)
        # self.play(Transform(label_definition_example_label_rep_group, label_definition_example_label_rep_group_new))
        # self.next_slide(notes="And if two labels has the same color, it means they have the same attribute name.")
        # label_definition_example_label_rep_3 = self.label_rep[1].copy().scale(1.5).next_to(
        #     label_definition_example_label_rep_group, RIGHT, buff=2)
        # label_definition_example_label_rep_group.add(label_definition_example_label_rep_3)
        # label_definition_example_label_rep_group_new = (label_definition_example_label_rep_group
        #                                                 .copy().arrange(RIGHT, buff=1))
        # label_definition_example_label_rep_group_new.move_to(ORIGIN + UP * 3)
        # self.play(Transform(label_definition_example_label_rep_group, label_definition_example_label_rep_group_new))
        # self.next_slide(notes="And if two labels has different color, "
        #                       "it means they have the different attribute name.\n\n"
        #                       "The attribute value assignment is displayed in the center.")
        self.next_slide(notes="Now let's represent the entries attribute with the labels.")
        example_document_new = make_document_rep(self.documents[1], icon_template=None, show_text=False)
        self.play(Transform(example_document, example_document_new),
                  FadeOut(label_definition_example_rep))
        self.next_slide(notes="Let's now put everything together. Here we have the embedding vectors.")
        vector_explain_text = Text("Embedding Vector", font_size=72).next_to(example_document, LEFT, buff=1)
        vector_explain_arrow = Arrow(vector_explain_text.get_right() + RIGHT * .3, example_document[1].get_left(),
                                     buff=0)
        self.play(FadeIn(vector_explain_arrow, vector_explain_text))
        self.next_slide(notes="Let's now put everything together. Here we have the embedding vectors.\n\n"
                              "And the labels.")
        label_explain_text = Text("Label", font_size=72).next_to(example_document, RIGHT, buff=1.5)
        label_explain_arrow_1 = Arrow(label_explain_text.get_left() + LEFT * .3, example_document_new[2][0].get_right(),
                                      buff=0)
        label_explain_arrow_2 = Arrow(label_explain_text.get_left() + LEFT * .3, example_document_new[2][1].get_right(),
                                      buff=0)
        label_explain_arrow_3 = Arrow(label_explain_text.get_left() + LEFT * .3, example_document_new[2][2].get_right(),
                                      buff=0)
        self.play(FadeIn(label_explain_arrow_1, label_explain_arrow_2, label_explain_arrow_3, label_explain_text))
        self.next_slide(notes="Then we define the label set of an entry as the sets of it's label.")
        label_set_explain_rect = SurroundingRectangle(example_document[2], buff=.2, color=YELLOW)
        label_set_explain_text = Text("Label Set", font_size=72).next_to(label_set_explain_rect, UP, buff=1.5)
        label_set_explain_arrow = Arrow(label_set_explain_text.get_bottom() + DOWN * .3,
                                        label_set_explain_rect.get_top(), buff=0)
        self.play(self._set_title("Define Label Set"),
                  DrawBorderThenFill(label_set_explain_rect),
                  FadeIn(label_set_explain_arrow, label_set_explain_text))

        # show a list of documents
        self.next_slide(notes="Now let's consider all entries in the dataset, "
                              "each entry have a corrosponding label set according to our definition.")
        documents_rep_list = []
        last_rep = None
        for idx, document_dict in sorted(self.documents.items(), key=lambda t: t[0], reverse=True):
            rep = make_document_rep(document_dict)
            if last_rep is not None:
                rep.align_to(last_rep, DL).shift(UP * .6)
            else:
                rep.to_edge(LEFT).shift(DOWN * 6.6)
            rep.set_z_index(len(self.documents) - idx)
            last_rep = rep
            documents_rep_list.append(rep)
        self.play(FadeOut(vector_explain_arrow, vector_explain_text,
                          label_explain_arrow_1, label_explain_arrow_2, label_explain_arrow_3, label_explain_text,
                          label_set_explain_rect, label_set_explain_arrow, label_set_explain_text))
        self.play(self._set_title("Label Sets"),
                  *TransformTo(example_document, documents_rep_list[-1]), FadeIn(*documents_rep_list[:-1]))
        self.next_slide(notes="Here are all the unique label sets in our dataset.")

        # group documents by label set
        label_set_rep_list = [rep.copy() for rep in self.label_set_reps]
        label_set_rep = VGroup(*label_set_rep_list)
        label_set_rep.arrange(DOWN, buff=1)
        self.play(FadeIn(label_set_rep))
        self.next_slide(notes="Next, let's group the vectors by the unique label sets.")
        label_set_rep_new = label_set_rep.copy()
        label_set_rep_new.arrange(DOWN, buff=1, aligned_edge=RIGHT)
        label_set_rep_new.shift(LEFT * 6)
        self.play(Transform(label_set_rep, label_set_rep_new))
        label_set_rep_last_entry = label_set_rep_list[:]
        document_vector_rep_list = []
        document_to_vector_animations = []
        for idx, document_dict in sorted(self.documents.items(), key=lambda t: t[0]):
            document_rep = documents_rep_list[-idx]
            document_vector_rep = NodeGraph.make_graph_nodes(document_dict["name"])
            destination_label_set_index = document_dict["label_set"]["id"] - 1
            document_vector_rep.next_to(label_set_rep_last_entry[destination_label_set_index], RIGHT, buff=1)
            label_set_rep_last_entry[destination_label_set_index] = document_vector_rep
            document_vector_rep_list.append(document_vector_rep)
            document_to_vector_animations.append(TransformTo(document_rep, document_vector_rep))
        self.play(*document_to_vector_animations[0])
        self.next_slide(notes="Next, let's group the vectors by the unique label sets.")
        self.play(*document_to_vector_animations[1])
        self.next_slide(notes="Next, let's group the vectors by the unique label sets.\n\n"
                              "Notice that each vector have a unique label set, so this essentially allows us to "
                              "partition the dataset into sets of vectors that are disjoint, "
                              "where each label set owns a unique partition.")
        for anims in document_to_vector_animations[2:]:
            self.play(*anims, run_time=.25)

        # determine supersets
        self.next_slide(notes="Now, let's focus on the label sets.")
        label_set_rep_new = label_set_rep.copy()
        label_set_rep_new.arrange(DOWN, buff=1)
        label_set_rep_new.move_to(ORIGIN)
        self.play(self._set_title("Label Sets Relationship"),
                  FadeOut(*document_vector_rep_list), Transform(label_set_rep, label_set_rep_new))
        self.next_slide(notes="More specifically, these three label sets...\n\n"
                              "Does anyone notices anything related to those sets?")
        highlight_target = [3, 2, 5]
        highlight_rect = [SurroundingRectangle(label_set_rep[idx - 1], color=YELLOW, buff=.25)
                          for idx in highlight_target]
        self.play(*[DrawBorderThenFill(rect) for rect in highlight_rect])
        self.next_slide(notes="More specifically, these three label sets...\n\n"
                              "Does anyone notices anything related to those sets?\n\n"
                              "Let's zoom in on those.")
        superset_label_sets_rep = VGroup(*[self.label_set_reps[idx - 1].copy() for idx in highlight_target])
        superset_label_sets_rep.arrange(UP, buff=4)
        superset_label_sets_rep.move_to(ORIGIN)
        self.play(FadeOut(*highlight_rect), Transform(label_set_rep, superset_label_sets_rep))
        self.next_slide(notes="There are some set containment relationships between them, or supersets.\n\n"
                              "Note that, what this really means is that some entries in the dataset have missing "
                              "attribute values...")
        superset_relations = [(0, 1), (1, 2), (0, 2)]
        superset_label_sets_superset_rel_supersets = []
        superset_label_sets_superset_rel_animations = []
        for f, t in superset_relations:
            if t - f == 1:
                arrow = Arrow(superset_label_sets_rep[f].get_top(), superset_label_sets_rep[t].get_bottom())
                text = Text(r"Superset", font_size=54).next_to(arrow, LEFT, buff=.5)
            else:
                arrow = CurvedArrow(superset_label_sets_rep[f].get_right() + RIGHT * .5,
                                    superset_label_sets_rep[t].get_right() + RIGHT * .5,
                                    angle=PI / 2)
                text = Text(r"Superset", font_size=54).next_to(arrow, RIGHT, buff=.5)
            superset_label_sets_superset_rel_supersets.append([arrow, text])
            superset_label_sets_superset_rel_animations.append((FadeIn(arrow), FadeIn(text)))
        self.play(self._set_title("Label Sets Relationship: Set Containment (aka. Superset)"),
                  *[anim for anims in superset_label_sets_superset_rel_animations for anim in anims])
        self.next_slide(notes="The paper focuses on the minimum supersets, which are defined as the supersets pairs "
                              "that doesn't have another superset in between of them.\n\n"
                              "Show example...")
        superset_label_sets_superset_rel_animations = []
        for idx, (f, t) in enumerate(superset_relations):
            if t - f == 1:
                arrow = superset_label_sets_superset_rel_supersets[idx][0].copy().set_color(GREEN)
                text = Text(r"Minimum Superset", font_size=54).set_color(GREEN)
                text.next_to(superset_label_sets_superset_rel_supersets[idx][0], LEFT, buff=.5)
                superset_label_sets_superset_rel_animations.append(
                    Transform(superset_label_sets_superset_rel_supersets[idx][1], text))
                superset_label_sets_superset_rel_animations.append(
                    Transform(superset_label_sets_superset_rel_supersets[idx][0], arrow))
        self.play(self._set_title("Label Sets Relationship: Minimum Superset"),
                  *superset_label_sets_superset_rel_animations)
        self.next_slide()
        self.play(FadeOut(*superset_label_sets_superset_rel_supersets[-1]))

        return {
            "cleanup_animations": (
                FadeOut(*[cc for c in superset_label_sets_superset_rel_supersets[:-1] for cc in c]),),
            "label_set_rep": label_set_rep
        }

    def section_2(self, cleanup_animations=None, label_set_rep=None):
        # Label Navigating Graph
        self.next_slide(notes="Given that, let's now define Label Navigating Graph, which is also the paper's core "
                              "intuition. Here are all the label sets.")
        label_set_layers = [[5, 7], [2, 6, 4], [3, 8, 1]]
        label_set_gap_list = [[4], [3, 7], [2, 2]]
        label_navigating_graph_rep = VGroup()
        for layer_idx, label_set_l in enumerate(label_set_layers):
            layer_label_sets = [
                LabelNode(self.label_set_reps[label_set_idx - 1], name=self.label_sets[label_set_idx]["rep_name"])
                for label_set_idx in label_set_l]
            last_set = None
            gap_index = 0
            for label_sets in layer_label_sets:
                if last_set is not None:
                    label_sets.next_to(last_set, RIGHT, buff=label_set_gap_list[layer_idx][gap_index])
                    gap_index += 1
                last_set = label_sets
            layer_label_set_rep = VGroup(*layer_label_sets)
            label_navigating_graph_rep.add(layer_label_set_rep)
        label_navigating_graph_rep.arrange(DOWN, buff=5)
        label_navigating_graph_rep.move_to(ORIGIN)
        animations = []
        if cleanup_animations is not None:
            animations.append(*cleanup_animations)
        if label_set_rep is not None:
            animations.append(FadeOut(label_set_rep))
            animations.append(FadeIn(label_navigating_graph_rep))
        else:
            animations.append(FadeIn(label_navigating_graph_rep))
        self.play(self._set_title("Label Navigating Graph"),
                  *animations)

        # Highlight previous examples
        self.next_slide(notes="These three are the label sets that we have seen in previous example.")
        lng_edges = EdgeManager(label_navigating_graph_rep)
        highlight_target = [3, 2, 5]
        highlight_edges = [("f3", "f2"), ("f2", "f5")]
        highlight_edges_others = [("f8", "f6"), ("f1", "f6"), ("f6", "f5"), ("f1", "f7"), ("f4", "f7")]
        highlight_reverse_edges = [(t, f) for f, t in highlight_edges]
        highlight_reverse_edges_others = [(t, f) for f, t in highlight_edges_others]
        highlight_target_name = [self.label_sets[idx]["rep_name"] for idx in highlight_target]
        highlight_rect = [SurroundingRectangle(*lng_edges.get_objects(name), color=YELLOW, buff=.25)
                          for name in highlight_target_name]
        self.play(*[DrawBorderThenFill(rect) for rect in highlight_rect])
        self.next_slide(notes="Recall that, here are the minimum supersets relationships for them.")
        highlight_arrows = lng_edges.add_edges(*highlight_edges, *highlight_edges_others,
                                               connect_top_to_bot=True, pos_buff=.25, buff=0, stroke_width=8,
                                               tip_width=.5, color=GREEN)
        self.play(*lng_edges.grow_edges(*highlight_edges))
        highlight_texts = [Text("Minimum Superset", font_size=54, color=GREEN).next_to(arrow, LEFT, buff=.3)
                           for arrow in highlight_arrows[:2]]
        highlight_texts[1].shift(RIGHT * 3 + UP * .5)
        self.play(FadeIn(*highlight_texts))
        self.next_slide(notes="Let's add in the minimum superset relationships for the rest of the label sets.")
        legend = make_legend(*self.legend_configs[0:2]).to_edge(UP).shift(RIGHT * 14 + DOWN * 3)
        self.play(FadeOut(*highlight_rect), FadeIn(legend),
                  *lng_edges.grow_edges(*highlight_edges_others))
        self.next_slide(notes="Now, we are going add edges in the LNG graph "
                              "according to the minimum superset relationship.\n\n"
                              "More specifically, we want to add edges in the reverse direction of minimum superset "
                              "relationship between two label sets, so from the subset to it's supersets.")
        lng_edges.add_edges(*self.lng_edges,
                            connect_bot_to_top=True, pos_buff=.25, buff=0, stroke_width=8, tip_width=.5, color=ORANGE)
        self.play(FadeOut(*highlight_texts), lng_edges.fadeOut_edges(*highlight_edges),
                  *lng_edges.grow_edges(*highlight_reverse_edges))
        self.next_slide(notes="Let's do that for all label sets, and here are the result.")
        self.play(lng_edges.fadeOut_edges(*highlight_edges_others),
                  *lng_edges.grow_edges(*highlight_reverse_edges_others))
        lng_edges.remove_edges(*highlight_edges, *highlight_edges_others)

        # Demonstrate the properties that allows traversals that won't touch any other sets
        self.next_slide(notes="Here, I want to highlight one important property of the LNG graph, "
                              "which is that if we start from any node in the LNG graph, all the node that we can reach"
                              "are supersets of the starting node.\n\n"
                              "Well this is trivial given how we constructed the graph, the edges always points "
                              "to supersets.\n\n"
                              "This is related to how the paper meet the fidelity requirement we talked before.\n\n"
                              "So by starting from a label set that meets the query label set, all nodes we can reach "
                              "also preserves the query filter.")
        legend_new = make_legend(self.legend_configs[1]).to_edge(UP).shift(RIGHT * 14 + DOWN * 3)
        highlight_nodes = [["f5"], ["f2", "f6"], ["f3", "f8", "f1"]]
        highlight_edges = [[("f5", "f2"), ("f5", "f6")], [("f2", "f3"), ("f6", "f8"), ("f6", "f1")]]
        # highlight_rect = [[SurroundingRectangle(*lng_edges.get_objects(n), color=YELLOW, buff=.25) for n in nn]
        #                   for nn in highlight_nodes]
        fidelity_description_text = Text("Fidelity: Should only touch the vectors that satisfy the filter.",
                                         font_size=72)
        fidelity_description_text.to_edge(DOWN)
        self.play(Transform(legend, legend_new),
                  # *lng_edges.highlight_nodes(*[n for nn in highlight_nodes for n in nn]),
                  # *lng_edges.highlight_edges(*[e for ee in highlight_edges for e in ee]),
                  self._set_title("Label Navigating Graph: Fidelity"),
                  Write(fidelity_description_text))
        self.next_slide(
            notes="For example, if you start the traversal at the label set of only the label venue=SIGMOD.")
        highlight_start_node = [*lng_edges.get_objects(highlight_nodes[0][0])][0]
        highlight_start_arrow = Arrow(highlight_start_node.get_top() + UP * 2, highlight_start_node.get_top(),
                                      stroke_width=8)
        self.play(FadeIn(highlight_start_arrow), *lng_edges.fadeOut_edges(all=True))
        self.next_slide(notes="All the nodes that you touches satisfy are all supersets of your starting label set. So "
                              "they all contains the label SIGMOD.")
        for idx in range(3):
            if idx != 0:
                self.play(*lng_edges.grow_edges(*highlight_edges[idx - 1]), run_time=2)
            self.play(*[Indicate(obj, scale_factor=1.2) for obj in lng_edges.get_objects(*highlight_nodes[idx])],
                      # *[DrawBorderThenFill(rect) for rect in highlight_rect[idx]],
                      run_time=1)
        self.next_slide(notes="All the nodes that you touches satisfy are all supersets of your starting label set. "
                              "So they all contains the label SIGMOD.")
        self.play(Circumscribe(*lng_edges.get_objects(highlight_nodes[0][0]), buff=.25),
                  # Indicate(highlight_rect[0][0], scale_factor=1.2)
                  run_time=1
                  )
        self.play(*[Circumscribe(*lng_edges.get_objects(n), buff=.25) for nn in highlight_nodes[1:] for n in nn],
                  # *[Indicate(r, scale_factor=1.2) for rr in highlight_rect[1:] for r in rr]
                  run_time=1
                  )
        # self.play(*lng_edges.undo_highlight_nodes(*[n for nn in highlight_nodes for n in nn]),
        #           *lng_edges.undo_highlight_edges(*[e for ee in highlight_edges for e in ee]),
        #           FadeOut(*[r for rr in highlight_rect for r in rr]))
        # self.next_slide()

        return {
            "cleanup_animations": (
                FadeOut(*lng_edges.get_edges(*[e for ee in highlight_edges for e in ee])),
                FadeOut(highlight_start_arrow),
                FadeOut(fidelity_description_text),
                FadeOut(legend)),
            "label_navigating_graph_rep": label_navigating_graph_rep,
            "lng_edges": lng_edges,
        }

    def section_3(self, cleanup_animations=None, label_navigating_graph_rep=None, lng_edges=None):
        # clean up
        self.next_slide(notes="Next, let see how shall we incorporate the vectors into this graph.")
        if cleanup_animations is not None:
            self.play(*cleanup_animations)
        self.play(self._set_title("Label Navigating Graph"))

        # Unified Navigating Graph
        self.next_slide(notes="Recall that each label set correspond to a unique set of vectors.\n\n"
                              "Here are the vectors.")
        label_set_layers = [[5, 7], [2, 6, 4], [3, 8, 1]]
        label_set_gap_list = [[4], [3, 7], [2, 2]]
        graph_hg = 5
        graph_param = [[{"box_size": (5, graph_hg)}, {"box_size": (5, graph_hg)}],
                       [{"box_size": (10, graph_hg)}, {"box_size": (7.5, graph_hg)}, {"box_size": (8, graph_hg)}],
                       [{"box_size": (13.5, graph_hg)}, {"box_size": (13, graph_hg)}, {"box_size": (9.5, graph_hg)}]]
        unified_navigating_graph_rep = VGroup()
        for layer_idx, label_set_l in enumerate(label_set_layers):
            layer_graphs = []
            for label_set_idx, param in zip(label_set_l, graph_param[layer_idx]):
                label_set_info = self.label_sets[label_set_idx]
                graph = NodeGraph(label_set_info["rep_name"],
                                  label_set_info["label_set_rep"],
                                  label_set_info["nodes"],
                                  box_padding=1, bot_padding=1,
                                  **param)
                layer_graphs.append(graph)
            last_graph = None
            gap_index = 0
            for graph in layer_graphs:
                if last_graph is not None:
                    graph.next_to(last_graph, RIGHT, buff=label_set_gap_list[layer_idx][gap_index])
                    gap_index += 1
                last_graph = graph
            layer_label_set_rep = VGroup(*layer_graphs)
            unified_navigating_graph_rep.add(layer_label_set_rep)
        unified_navigating_graph_rep.arrange(DOWN, buff=1.5)
        unified_navigating_graph_rep.move_to(ORIGIN).shift(DOWN * 1)
        animations = []
        if label_navigating_graph_rep is not None and lng_edges is not None:
            # add pairwise transformation from LNG nodes to UNG nodes
            temp_edge_manager = EdgeManager(unified_navigating_graph_rep)
            for layer_idx, label_set_l in enumerate(label_set_layers):
                for label_set_idx, param in zip(label_set_l, graph_param[layer_idx]):
                    label_set_info = self.label_sets[label_set_idx]
                    lng_node = [*lng_edges.get_objects(label_set_info["rep_name"])][0]
                    ung_node = [*temp_edge_manager.get_objects(label_set_info["rep_name"])][0]
                    animations.append(Transform(lng_node, ung_node))
        else:
            animations.append(FadeIn(unified_navigating_graph_rep))
            label_navigating_graph_rep = unified_navigating_graph_rep
        self.play(*animations)

        # connect subgraph edges
        self.next_slide(notes="For each set of vectors sharing the same label set, "
                              "we build a proximity-based navigation graph, "
                              "which can actually follow any graph-based vector index design.\n\n")
        legend = make_legend(self.legend_configs[2])
        legend.to_edge(UP).shift(RIGHT * 15 + DOWN * 4.25)
        lng_edges = EdgeManager(unified_navigating_graph_rep)
        ung_inner_graph_edges = EdgeManager(unified_navigating_graph_rep)
        ung_cross_group_edges = EdgeManager(unified_navigating_graph_rep)
        lng_edges.add_edges(
            *self.lng_edges,
            connect_bot_to_top=True, pos_buff=.25, buff=0, stroke_width=8, tip_width=.5, color=ORANGE)
        ung_inner_graph_edges.add_edges(*self.ung_inner_graph_edges, color=BLUE)
        self.play(self._set_title("Unified Navigating Graph"),
                  FadeIn(legend),
                  ung_inner_graph_edges.fadeIn_edges(all=True))
        self.next_slide(notes="Now, each subgraphs itself are connected, let's connect each subgraphs.\n\n"
                              "Remember the LNG that we built on top of the label set containment relationship? "
                              "We will use those to connect the subgraphs together.")
        new_legend = make_legend(self.legend_configs[4], self.legend_configs[2])
        new_legend.to_edge(UP).shift(RIGHT * 15 + DOWN * 4)
        self.play(self._set_title("Unified Navigating Graph: Connecting Sub-graphs"),
                  Transform(legend, new_legend),
                  lng_edges.grow_edges(all=True))
        self.next_slide(notes="The cross group edges are added with these two specific rules...")
        cross_group_edges_description = make_multiline_text(
            r"Rules for adding Cross-Group Edges:",
            r"(1) Connect to the top-$\delta$ nearest vectors",
            r"out of vectors from it's Minimum Supersets",
            r"(2) Ensure at least $\delta$ cross-group edge",
            r"connecting all pairs of Minimum Superset",
            font_size=72, buff=[.75, .1, .75, .1])
        cross_group_edges_description.to_edge(LEFT).shift(UP * 8)
        cross_group_edges_description_line_1_rect = SurroundingRectangle(cross_group_edges_description[1],
                                                                         cross_group_edges_description[2],
                                                                         buff=.25, color=YELLOW)
        cross_group_edges_description_line_2_rect = SurroundingRectangle(cross_group_edges_description[3],
                                                                         cross_group_edges_description[4],
                                                                         buff=.25, color=YELLOW)
        new_legend = make_legend(self.legend_configs[4], self.legend_configs[3], self.legend_configs[2])
        new_legend.to_edge(UP).shift(RIGHT * 15 + DOWN * 3.75)
        self.play(self._set_title("Unified Navigating Graph: Adding Cross-Group Edges"),
                  Transform(legend, new_legend),
                  FadeIn(cross_group_edges_description))
        self.next_slide(notes="The cross group edges are added with these two specific rules...")
        self.play(DrawBorderThenFill(cross_group_edges_description_line_1_rect))
        self.next_slide(notes="The cross group edges are added with these two specific rules...")
        self.play(FadeOut(cross_group_edges_description_line_1_rect),
                  DrawBorderThenFill(cross_group_edges_description_line_2_rect))

        # show a demo
        self.next_slide(notes="Let's zoom in onto this part, and see it in detail.")
        old_unified_navigating_graph_rep = unified_navigating_graph_rep.copy()
        highlight_lng_edges = [("f5", "f2"), ("f5", "f6")]
        highlight_lng_nodes = ["f5", "f2", "f6"]
        demo_unified_navigating_graph_rep = VGroup(*[obj.copy() for obj in lng_edges.get_objects(*highlight_lng_nodes)])
        self.play(FadeOut(cross_group_edges_description_line_2_rect),
                  *lng_edges.fadeOut_edges(all=True),
                  *ung_inner_graph_edges.fadeOut_edges(all=True),
                  FadeOut(label_navigating_graph_rep))  # fading out UNG
        self.play(cross_group_edges_description.animate.scale(1.2).to_edge(LEFT).shift(DOWN * 1.5),
                  demo_unified_navigating_graph_rep.animate.scale(1.4).shift(DOWN * 3, RIGHT * 6))
        cross_group_edges_description_line_1_rect = SurroundingRectangle(cross_group_edges_description[1],
                                                                         cross_group_edges_description[2],
                                                                         buff=.25, color=YELLOW)
        cross_group_edges_description_line_2_rect = SurroundingRectangle(cross_group_edges_description[3],
                                                                         cross_group_edges_description[4],
                                                                         buff=.25, color=YELLOW)
        demo_edges = EdgeManager(demo_unified_navigating_graph_rep)
        demo_edges.add_edges(
            *highlight_lng_edges,
            connect_bot_to_top=True, pos_buff=.25, buff=0, stroke_width=8, tip_width=.5, color=ORANGE)
        self.play(self._set_title(r"Unified Navigating Graph: Adding Cross-Group Edges ($\delta = 1$)"),
                  *demo_edges.fadeIn_edges(*highlight_lng_edges))
        all_connection_nodes = ["v11", "v12", "v2", "v13", "v14", "v15"]

        def _sync_cross_group_edges_description_state(line_1, line_2):
            anim = []
            if self.cross_group_edges_description_line_1_flag != line_1:
                if line_1:
                    anim.append(FadeIn(cross_group_edges_description_line_1_rect))
                else:
                    anim.append(FadeOut(cross_group_edges_description_line_1_rect))
                self.cross_group_edges_description_line_1_flag = line_1
            if self.cross_group_edges_description_line_2_flag != line_2:
                if line_2:
                    anim.append(FadeIn(cross_group_edges_description_line_2_rect))
                else:
                    anim.append(FadeOut(cross_group_edges_description_line_2_rect))
                self.cross_group_edges_description_line_2_flag = line_2
            return anim

        def _demo_select_cross_group_edge(node, cleanup_animation=None):
            highlight_nodes = [node] + all_connection_nodes
            connection_edges = [(node, t) for t in all_connection_nodes]
            target_edge = [*filter_edges(self.ung_cross_group_edges, f=[node])]
            edges = EdgeManager(demo_unified_navigating_graph_rep)
            edges.add_edges(*connection_edges, style=DASHED, color=ORANGE, stroke_width=10, buff=.75, tip_width=.5)
            anim = []
            if cleanup_animation is not None:
                anim.extend(cleanup_animation)
            anim.extend(_sync_cross_group_edges_description_state(True, False))
            self.next_slide(notes="Now, according to rule 1, for Delta = 1, we need to pick the nearest one vector "
                                  "(in terms of proximity) from these candidate.\n\n"
                                  "In terms of implementation, since we have a graph index for each subgraph, we can "
                                  "essentially issues KNN queries to find the top-Delta closest vector, and this can be "
                                  "performed parallely, since we are not modifying the subgraph index.")
            self.play(*anim,
                      *edges.fadeOut_nodes(*highlight_nodes, inverse=True),
                      *edges.fadeIn_edges(all=True))
            self.next_slide(notes="This is the closest vector in this example, we simply connect them.", loop=True)
            self.play(*edges.wave_edges(target_edge[0]))
            self.next_slide(notes="This is the closest vector in this example, we simply connect them.")
            self.play(*edges.fadeOut_edges(target_edge[0], inverse=True))
            target_edge_idx = 1
            while target_edge_idx < len(target_edge):
                second_target = target_edge[target_edge_idx]
                self.next_slide(
                    notes="Another condition that we need to meet is that: we need to ensure at least one edge are "
                          "added to each minimum supersets, to ensure connectivity of the unified navigating graph.")
                self.play(*_sync_cross_group_edges_description_state(False, True))
                self.play(*edges.fadeIn_edges(second_target))
                target_edge_idx += 1
            return (*edges.fadeIn_nodes(*highlight_nodes, inverse=True),
                    *edges.fadeOut_edges(*target_edge))

        self.next_slide(notes="Here are the cross-group edges being added.")
        cleanup_anim = [*demo_edges.fadeOut_edges(*highlight_lng_edges)]
        cleanup_anim = _demo_select_cross_group_edge("v6", cleanup_animation=cleanup_anim)
        cleanup_anim = _demo_select_cross_group_edge("v7", cleanup_animation=cleanup_anim)
        cleanup_anim = _demo_select_cross_group_edge("v5", cleanup_animation=cleanup_anim)
        self.next_slide(notes="So here, we need to add one more edges to ensure rule 2 is valid.")
        self.play(*cleanup_anim, *_sync_cross_group_edges_description_state(False, False))
        demo_added_cross_group_edges = [*filter_edges(self.ung_cross_group_edges, f=["v6", "v7", "v5"])]
        demo_edges.add_edges(
            *demo_added_cross_group_edges, style=DASHED, color=ORANGE, stroke_width=10, buff=.75, tip_width=.5)
        self.play(*demo_edges.fadeIn_edges(*demo_added_cross_group_edges))
        self.next_slide(notes="Here are the inner edges for each subgraph. "
                              "And now that's everything we are going to add for this portion of the graph.")
        demo_added_ung_inner_edges = [*filter_edges(self.ung_inner_graph_edges,
                                                    f=["v6", "v7", "v5"] + all_connection_nodes)]
        demo_edges.add_edges(
            *demo_added_ung_inner_edges, color=BLUE, stroke_width=10, buff=.75, tip_width=.5)
        self.play(*demo_edges.fadeIn_edges(*demo_added_ung_inner_edges))

        # completeness
        self.next_slide(
            notes="Note, the rule 2 ensures that the UNG graph is connected, such that if you start a "
                  "traversal from a label set, you can eventually reach all it's supersets.\n\n"
                  "This is related to ensuring the completeness property:\n\n"
                  "Assuming a subgraph index with good connectivity, "
                  "meaning you can reach all vectors from the entry vectors.\n"
                  "And since rule 2 ensures that at least Delta cross-group edge is connected between any minimum "
                  "superset pair, this means we can reach at least Delta nodes in the superset nodes, and so on.\n\n"
                  "So in the end, you can reach at least Delta vectors, so you can tune the Delta parameter to ensure "
                  "completeness.\n\n"
                  "And the paper also mentioned that completeness can typically be archived for Delta smaller than k.\n\n"
                  "Completeness is proven more rigorously in the paper.")
        completeness_text = Tex(
            r"Completeness: at least $\delta+1$ vectors matching the filter are reachable",
            font_size=72 * 1.25)
        completeness_text.to_edge(DOWN)
        self.play(Write(completeness_text))

        # return back to the whole graph view
        self.next_slide(notes="Let's overlay everything into one picture.")
        new_legend = make_legend(self.legend_configs[3], self.legend_configs[2])
        new_legend.to_edge(UP).shift(RIGHT * 15 + DOWN * 4)
        self.play(self._set_title("Unified Navigating Graph"),
                  *demo_edges.fadeOut_edges(*demo_added_ung_inner_edges, *demo_added_cross_group_edges),
                  FadeOut(demo_unified_navigating_graph_rep),
                  FadeOut(completeness_text),
                  FadeOut(cross_group_edges_description),
                  Transform(legend, new_legend))
        unified_navigating_graph_rep = old_unified_navigating_graph_rep
        unified_navigating_graph_edges = EdgeManager(unified_navigating_graph_rep)
        unified_navigating_graph_edges.add_edges(*self.ung_inner_graph_edges, color=BLUE)
        unified_navigating_graph_edges.add_edges(*self.ung_cross_group_edges, style=DASHED, color=ORANGE,
                                                 stroke_width=6)
        self.play(FadeIn(unified_navigating_graph_rep))
        self.play(unified_navigating_graph_edges.fadeIn_edges(*self.ung_inner_graph_edges))
        self.play(unified_navigating_graph_edges.fadeIn_edges(*self.ung_cross_group_edges))

        return {
            "legend": legend,
            "unified_navigating_graph_rep": unified_navigating_graph_rep,
            "unified_navigating_graph_edges": unified_navigating_graph_edges,
        }
        # return
        # v6_connection_edges = [("v6", "v11"), ("v6", "v12"), ("v6", "v2"), ("v6", "v13"), ("v6", "v14"), ("v6", "v15")]
        # v5_connection_edges = [("v5", "v11"), ("v5", "v12"), ("v5", "v2"), ("v5", "v13"), ("v5", "v14"), ("v5", "v15")]
        # v7_connection_edges = [("v7", "v11"), ("v7", "v12"), ("v7", "v2"), ("v7", "v13"), ("v7", "v14"), ("v7", "v15")]
        # demo_edges.add_edges(*v6_connection_edges, style=DASHED, color=ORANGE, stroke_width=6)
        # self.play(FadeIn(cross_group_edges_description_line_1_rect),
        #           *demo_edges.fadeOut_edges(*highlight_lng_edges),
        #           *demo_edges.fadeIn_edges(*v6_connection_edges))
        # self.next_slide(notes="Now, according to rule 1, for Delta = 1, we need to pick the nearest one vector "
        #                       "(in terms of proximity) from these candidate.")
        # self.play(*demo_edges.highlight_edges(v6_connection_edges[0]))
        # ung_cross_group_edges.cleanup_highlight_edges(v6_connection_edges[0])
        # self.play(*ung_cross_group_edges.fadeOut_edges(*v6_connection_edges[1:]))
        # ung_cross_group_edges.remove_edges(*v6_connection_edges[1:])
        # self.next_slide(notes="More specifically, for each vector in the subset, we pick the top-Delta nearest vectors "
        #                       "(in terms of proximity in the vector space) out of all vectors in it's minimum supersets."
        #                       "\n\nIn this case Delta = 1.\n\n")
        # ung_cross_group_edges.add_edges(*v7_connection_edges, style=DASHED, color=ORANGE, stroke_width=6)
        # self.play(*ung_cross_group_edges.fadeIn_edges(*v7_connection_edges))
        # self.play(*ung_cross_group_edges.highlight_edges(v7_connection_edges[0], v6_connection_edges[0]))
        # ung_cross_group_edges.cleanup_highlight_edges(v7_connection_edges[0], v6_connection_edges[0])
        # self.play(*ung_cross_group_edges.fadeOut_edges(*v7_connection_edges[1:]))
        # ung_cross_group_edges.remove_edges(*v7_connection_edges[1:])
        # self.next_slide()
        # ung_cross_group_edges.add_edges(*v5_connection_edges, style=DASHED, color=ORANGE, stroke_width=6)
        # self.play(*ung_cross_group_edges.fadeIn_edges(*v5_connection_edges))
        # self.play(*ung_cross_group_edges.highlight_edges(v5_connection_edges[2], v7_connection_edges[0],
        #                                                  v6_connection_edges[0]))
        # ung_cross_group_edges.cleanup_highlight_edges(v5_connection_edges[2], v7_connection_edges[0],
        #                                               v6_connection_edges[0])
        # self.play(*ung_cross_group_edges.fadeOut_edges(*v5_connection_edges[:2], *v5_connection_edges[3:]))
        # self.next_slide(notes="Another condition that we need to meet is that: we need to ensure at least one edge are "
        #                       "added to each minimum supersets, to ensure connectivity of the unified navigating graph."
        #                       "\n\n"
        #                       "In this case, note that v5's one-nearest-vector is v2, to ensure the "
        #                       "connectivity of the UNG, we need to add an additional edge, from v5 to v13.")
        # [*ung_cross_group_edges.get_edges(v5_connection_edges[3])][0].set_opacity(1)
        # self.play(*ung_cross_group_edges.fadeIn_edges(v5_connection_edges[3]))
        # ung_cross_group_edges.remove_edges(*v5_connection_edges[:2], *v5_connection_edges[4:])
        # self.next_slide(notes="Another condition that we need to meet is that: we need to ensure at least one edge are "
        #                       "added to each minimum supersets, to ensure connectivity of the unified navigating graph."
        #                       "\n\n"
        #                       "In this case, note that v5's one-nearest-vector is v2, to ensure the "
        #                       "connectivity of the UNG, we need to add an additional edge, from v5 to v13.")
        # ung_cross_group_edges_list = self.ung_cross_group_edges[:]
        # ung_cross_group_edges_list.remove(v5_connection_edges[2])
        # ung_cross_group_edges_list.remove(v5_connection_edges[3])
        # ung_cross_group_edges_list.remove(v7_connection_edges[0])
        # ung_cross_group_edges_list.remove(v6_connection_edges[0])
        # ung_cross_group_edges.add_edges(*ung_cross_group_edges_list, style=DASHED, color=ORANGE, stroke_width=6)
        # self.play(*ung_cross_group_edges.fadeIn_edges(v5_connection_edges[2], v5_connection_edges[3],
        #                                               v7_connection_edges[0], v6_connection_edges[0], inverse=True))
        # self.next_slide()
        # self.play(*ung_inner_graph_edges.fadeIn_edges(all=True))
        # self.next_slide()

    def query_example(self, query_vector_tex, query_filter_texts, query_labels, entry_label_sets,
                      legend, unified_navigating_graph_rep, unified_navigating_graph_edges: EdgeManager):
        anim = []
        self.next_slide(notes="Next, let's look at how to perform query.")
        if legend is not None and unified_navigating_graph_rep is not None and unified_navigating_graph_edges is not None:
            anim.append(FadeOut(legend))
            anim.append(FadeOut(unified_navigating_graph_rep))
            anim.extend(unified_navigating_graph_edges.fadeOut_edges(all=True))
        self.play(self._set_title("Unified Navigating Graph: Query"),
                  *anim)

        # show query
        self.next_slide(notes="Suppose we have a filtered ANNS query like this...")
        font_size = 72
        query_vector_rep = NodeGraph.make_graph_nodes(name=query_vector_tex, font_size=font_size, radius=.5)
        query_filter_rep = make_label_set_rep([Text(text, font_size=font_size) for text in query_filter_texts])
        query_label_set_rep = make_label_set_rep([self.label_rep[l_id - 1] for l_id in query_labels])
        entry_label_sets_rep = make_label_set_rep(
            [self.label_sets[l_id]["label_set_rep"] for l_id in entry_label_sets])
        raw_query_rep = VGroup(
            Text("SELECT * FROM vdbms", font_size=font_size),
            VGroup(Text("WHERE vec", font_size=font_size),
                   Text("<=>", font_size=font_size),
                   query_vector_rep.copy()).arrange(RIGHT, buff=.5),
            VGroup(Text("AND", font_size=font_size), query_filter_rep.copy()).arrange(RIGHT, buff=1),
        ).arrange(DOWN, buff=1, aligned_edge=LEFT)
        query_rep = VGroup(
            Text("SELECT * FROM vdbms", font_size=font_size),
            VGroup(Text("WHERE vec", font_size=font_size),
                   Text("<=>", font_size=font_size),
                   query_vector_rep.copy()).arrange(RIGHT, buff=.5),
            VGroup(Text("AND", font_size=font_size), query_label_set_rep.copy()).arrange(RIGHT, buff=.5),
        ).arrange(DOWN, buff=1, aligned_edge=LEFT)
        self.play(FadeIn(raw_query_rep))
        self.next_slide(notes="Let's represent the filter condition as labels.")
        self.play(Transform(raw_query_rep, query_rep))
        query_rep = raw_query_rep

        # versatility
        self.next_slide(notes="Notice, the label set abstraction provides versatility on the query filter, where "
                              "any size and combination of the attributes can be represented.")
        versatility_text = Text("Versatility: can represent filters of any size and combination of attributes",
                                font_size=font_size)
        versatility_text.next_to(query_rep[2][1], DOWN, buff=3)
        versatility_arrow = Arrow(versatility_text.get_top(), query_rep[2][1].get_bottom())
        self.play(Write(versatility_text), FadeIn(versatility_arrow))

        # step 1: find entry set
        self.next_slide(notes="Next, let's see how do we process the such query, with the label set as the filter.\n\n"
                              "First step is to find something called the \"Entry Sets\", which is where "
                              "we should start the graph search.\n\n"
                              "Intuitively, we should start at those that satisfies the filter, "
                              "which are just the supersets of the query label sets.")
        query_rep_new = query_rep.copy().shift(UP * 5)
        step_1_find_entry_set_rep = VGroup(
            Text("Step 1: Find Entry Sets of", font_size=font_size),
            query_label_set_rep.copy(),
            Text("in the LNG", font_size=font_size)
        ).arrange(RIGHT, buff=.5)
        step_1_find_entry_set_rep.next_to(query_rep_new, DOWN, buff=4)
        step_1_find_entry_set_arrow = Arrow(query_rep_new.get_bottom() + DOWN * .5,
                                            step_1_find_entry_set_rep.get_top() + UP * .5, stroke_width=8)
        self.play(self._set_title("UNG Query: Step 1, Find Entry Sets"),
                  FadeOut(versatility_text), FadeOut(versatility_arrow),
                  Transform(query_rep, query_rep_new),
                  FadeIn(step_1_find_entry_set_rep),
                  FadeIn(step_1_find_entry_set_arrow))
        self.next_slide(notes="There are two cases in finding the entry set.\n\n"
                              "Case 1 is the trivial case, which the query set directly matches one of the label set in LNG.\n"
                              "In this case, we can directly start from that set.\n\n"
                              "Case 2 is a bit more complicated.")
        step_1_find_entry_set_rep_new = step_1_find_entry_set_rep.copy().shift(UP * 8)
        entry_set_case_1 = Text("Case 1: matches an label set in an LNG exactly", font_size=font_size)
        entry_set_case_1.move_to(UP * .5)
        entry_set_case_2 = Text("Case 2: does not match any label sets in LNG", font_size=font_size)
        entry_set_case_2.next_to(entry_set_case_1, DOWN, buff=1, aligned_edge=LEFT)
        entry_set_case_brace = BraceBetweenPoints(entry_set_case_1.get_left(), entry_set_case_2.get_left(),
                                                  stroke_width=8)
        entry_set_case = VGroup(entry_set_case_1, entry_set_case_2, entry_set_case_brace)
        entry_set_case.next_to(step_1_find_entry_set_rep_new, DOWN, buff=4)
        self.play(FadeOut(query_rep), FadeOut(step_1_find_entry_set_arrow),
                  Transform(step_1_find_entry_set_rep, step_1_find_entry_set_rep_new),
                  FadeIn(entry_set_case))
        self.next_slide(notes="Trivially, handling case 2 would just require us to use all superset.\n\n"
                              "However, that may be too much.\n\n"
                              "We can start from the minimum supersets of the query label set, "
                              "all supersets are reachable by traversing the cross-group edge.\n\n"
                              "The paper introduces a method using Trie + Inverted List to efficiently find the "
                              "minimum superset of any query label set.")
        entry_set_case_2_rect = SurroundingRectangle(entry_set_case[1], buff=.25, color=YELLOW)
        entry_set_case_2_solution = VGroup(Text("Entry Sets = Minimum Supersets of", font_size=font_size),
                                           query_label_set_rep.copy(),
                                           Text("(Find using Trie + Inverted List!)", font_size=font_size))
        entry_set_case_2_solution.arrange(RIGHT, buff=.5)
        entry_set_case_2_solution.next_to(entry_set_case_2_rect, DOWN, buff=3)
        entry_set_case_2_solution_arrow = Arrow(entry_set_case_2_rect.get_bottom(), entry_set_case_2_solution.get_top(),
                                                stroke_width=8)
        self.play(DrawBorderThenFill(entry_set_case_2_rect),
                  Create(entry_set_case_2_solution),
                  FadeIn(entry_set_case_2_solution_arrow))
        self.next_slide(notes="And for this particular example, the entry set is ...")
        entry_set_case_2_solution_2 = VGroup(Text("Entry Sets =", font_size=font_size),
                                             entry_label_sets_rep.copy())
        entry_set_case_2_solution_2.arrange(RIGHT, buff=.5)
        entry_set_case_2_solution_2.next_to(entry_set_case_2_solution, DOWN, buff=3)
        entry_set_case_2_solution_2_arrow = Arrow(entry_set_case_2_solution.get_bottom(),
                                                  entry_set_case_2_solution_2.get_top(),
                                                  stroke_width=8)
        self.play(FadeIn(entry_set_case_2_solution_2),
                  FadeIn(entry_set_case_2_solution_2_arrow))

        # step 2: greedy best first search
        self.next_slide(
            notes="The next step is just to perform the greedy best first search from all nodes in the entry set's graph.")
        entry_set_case_2_solution_2_new = entry_set_case_2_solution_2.copy().move_to(
            step_1_find_entry_set_rep.get_center())
        self.play(self._set_title("UNG Query: Step 2, Greedy Best First Search"),
                  FadeOut(step_1_find_entry_set_rep),
                  FadeOut(entry_set_case),
                  FadeOut(entry_set_case_2_rect),
                  FadeOut(entry_set_case_2_solution),
                  FadeOut(entry_set_case_2_solution_arrow),
                  FadeOut(entry_set_case_2_solution_2_arrow),
                  Transform(entry_set_case_2_solution_2, entry_set_case_2_solution_2_new))
        self.next_slide(notes="We just follow the standard best-first search using the distance heuristic.\n\n"
                              "We start by populating the queue with entry vectors from the entry sets's subgraph index.\n"
                              "We select randomly, Sigma of them.\n\n"
                              "Then, each time, we pop the best vector based on the heuristic, and push all it's out-edges.\n"
                              "We also only keep the best W candidate to keep the search queue short.\n"
                              "Note that, the cross-group edges are also in the out-neighbour's list, so during this step,"
                              "we are exploring other partitions' graph, through these edge.\n\n"
                              "Lastly, the greedy search stops when all W candidate are explored.")
        step_2_solution = make_multiline_text(
            r"(1) Initialize queue with randomly selected $\sigma$ Entry Vectors from",
            r"Entry Set's graph indexes",
            r"(2) Each iteration, pop the nearest vector in queue and push all it's",
            r"out-neighbors, keeping the best $w>k$ candidates",
            r"(3) Greedy Search until the all $w$ vectors in queue are all explored",
            font_size=font_size * 1.25,
            buff=[.5, 1.5, .5, 1.5]
        )
        step_2_solution.next_to(entry_set_case_2_solution_2, DOWN, buff=3)
        step_2_solution_arrow = Arrow(entry_set_case_2_solution_2.get_bottom(),
                                      step_2_solution.get_top(),
                                      stroke_width=8)
        self.play(FadeIn(step_2_solution_arrow),
                  FadeIn(step_2_solution[0], step_2_solution[1]))
        self.next_slide(notes="We just follow the standard best-first search using the distance heuristic.\n\n"
                              "We start by populating the queue with entry vectors from the entry sets's subgraph index.\n"
                              "We select randomly, Sigma of them.\n\n"
                              "Then, each time, we pop the best vector based on the heuristic, and push all it's out-edges.\n"
                              "We also only keep the best W candidate to keep the search queue short.\n"
                              "Note that, the cross-group edges are also in the out-neighbour's list, so during this step,"
                              "we are exploring other partitions' graph, through these edge.\n\n"
                              "Lastly, the greedy search stops when all W candidate are explored.")
        self.play(FadeIn(step_2_solution[2], step_2_solution[3]))
        self.next_slide(notes="We just follow the standard best-first search using the distance heuristic.\n\n"
                              "We start by populating the queue with entry vectors from the entry sets's subgraph index.\n"
                              "We select randomly, Sigma of them.\n\n"
                              "Then, each time, we pop the best vector based on the heuristic, and push all it's out-edges.\n"
                              "We also only keep the best W candidate to keep the search queue short.\n"
                              "Note that, the cross-group edges are also in the out-neighbour's list, so during this step,"
                              "we are exploring other partitions' graph, through these edge.\n\n"
                              "Lastly, the greedy search stops when all W candidate are explored.")
        self.play(FadeIn(step_2_solution[4]))
        # step_2_solution_1 = Tex(
        #     r"Initialize queue with randomly selected $\sigma$ Entry Vectors from Entry Set's corresponding graph indexes",
        #     font_size=font_size * 1.25)
        # step_2_solution_1.next_to(entry_set_case_2_solution_2, DOWN, buff=3)
        # step_2_solution_1_arrow = Arrow(entry_set_case_2_solution_2.get_bottom(),
        #                                 step_2_solution_1.get_top(),
        #                                 stroke_width=8)
        # self.play(FadeIn(step_2_solution_1), FadeIn(step_2_solution_1_arrow))
        # self.next_slide(notes="")
        # step_2_solution_2 = Tex(
        #     "Each iteration, pop the nearest vector in queue and push all it's out-neighbors, keeping the best $w>k$ candidates",
        #     font_size=font_size * 1.25)
        # step_2_solution_2.next_to(step_2_solution_1, DOWN, buff=3)
        # step_2_solution_2_arrow = Arrow(step_2_solution_1.get_bottom(),
        #                                 step_2_solution_2.get_top(),
        #                                 stroke_width=8)
        # self.play(FadeIn(step_2_solution_2), FadeIn(step_2_solution_2_arrow))
        # self.next_slide(notes="")
        # step_2_solution_3 = Tex("Greedy Search until the all $w$ vectors in queue are all explored",
        #                         font_size=font_size * 1.25)
        # step_2_solution_3.next_to(step_2_solution_2, DOWN, buff=3)
        # step_2_solution_3_arrow = Arrow(step_2_solution_2.get_bottom(),
        #                                 step_2_solution_3.get_top(),
        #                                 stroke_width=8)
        # self.play(FadeIn(step_2_solution_3), FadeIn(step_2_solution_3_arrow))

        # putting together
        # self.next_slide(notes="Here, let's put everything together and show an example.\n\n"
        #                       "So to handle a filtered ANNS query, it's a two step process:\n"
        #                       "Step 1 would just be finding the entry sets\n"
        #                       "Step 2 does a traversal starting from the entry vectors of those subgraph indexes.")
        # query_rep_new = query_rep.copy().arrange(RIGHT, buff=.5).move_to(UP * 5)
        # step_1_find_entry_set_rep_new = step_1_find_entry_set_rep.copy().next_to(query_rep_new, DOWN, buff=4)
        # step_2_greedy_best_first_search = Text(
        #     "Step 2: Greedy BFS in UNG starting from random Entry Vectors from Entry Sets",
        #     font_size=font_size).next_to(step_1_find_entry_set_rep_new, DOWN, buff=.5)
        # step_1_arrow = Arrow(query_rep_new.get_bottom() + DOWN * .5,
        #                      step_1_find_entry_set_rep_new.get_top() + UP * .5, stroke_width=8)
        # query_workflow_rep = VGroup(step_1_arrow, step_1_find_entry_set_rep_new,
        #                             step_2_greedy_best_first_search)
        # self.play(self._set_title("UNG Query: Example"),
        #           FadeOut(step_2_solution, step_2_solution_arrow),
        #           FadeOut(entry_set_case_2_solution_2),
        #           FadeIn(query_rep_new),
        #           FadeIn(query_workflow_rep))
        # query_rep = query_rep_new

        # query example
        if legend is None or unified_navigating_graph_rep is None or unified_navigating_graph_edges is None:
            return
        self.next_slide(notes="Let's see an example...")
        new_query_workflow_rep = make_multiline_text(
            r"Step 1: Find Entry Sets",
            r"Step 2: Greedy BFS",
            font_size=font_size * 1.25,
        )
        new_query_workflow_rep.to_edge(LEFT).shift(UP * 6.5, RIGHT * 1.5)
        query_workflow_rep_line_1 = SurroundingRectangle(new_query_workflow_rep[0],
                                                         buff=.25, color=YELLOW)
        query_workflow_rep_line_2 = SurroundingRectangle(new_query_workflow_rep[1],
                                                         buff=.25, color=YELLOW)
        query_rep_new = query_rep.copy().arrange(RIGHT, buff=.5)
        self.play(*self._set_title_as_new_object(query_rep_new),
                  FadeIn(legend),
                  FadeOut(entry_set_case_2_solution_2, step_2_solution, step_2_solution_arrow),
                  FadeIn(unified_navigating_graph_rep),
                  FadeIn(new_query_workflow_rep))
        self.title = query_rep_new

        # query example: step 1, find entry set
        self.next_slide(notes="Here are the entry sets.")
        unified_navigating_graph_objects = EdgeManager(unified_navigating_graph_rep)
        entry_nodes = [self.label_sets[l_id]["rep_name"] for l_id in entry_label_sets]
        entry_vectors = [self.documents[self.label_sets[l_id]["entry_vector"]]["rep_name"] for l_id in entry_label_sets]
        entry_nodes_text = Text("Entry Sets", font_size=font_size).shift(UP * 4, LEFT * 2)
        entry_nodes_text_arrows = []
        for i, entry_node in enumerate(entry_nodes):
            node = [*unified_navigating_graph_objects.get_objects(entry_node)][0]
            arrow = Arrow(entry_nodes_text.get_bottom(), node.get_top(), stroke_width=8, color=YELLOW)
            entry_nodes_text_arrows.append(arrow)
        entry_nodes_text_rep = VGroup(entry_nodes_text, *entry_nodes_text_arrows)
        self.play(DrawBorderThenFill(query_workflow_rep_line_1),
                  *unified_navigating_graph_edges.highlight_nodes(*entry_nodes),
                  FadeIn(entry_nodes_text_rep))
        self.next_slide(notes="Here are the selected entry vectors.")
        entry_vector_text = Text("Entry Vectors", font_size=font_size).shift(DOWN * 10, LEFT * 10)
        entry_vector_text_arrows = []
        for i, entry_vector in enumerate(entry_vectors):
            node = [*unified_navigating_graph_objects.get_objects(entry_vector)][0]
            arrow = Arrow(entry_vector_text.get_top(), node.get_center(), buff=.5, stroke_width=8, color=YELLOW)
            entry_vector_text_arrows.append(arrow)
        entry_vector_text_rep = VGroup(entry_vector_text, *entry_vector_text_arrows)
        self.play(FadeIn(entry_vector_text_rep))
        self.next_slide(notes="Let's next see an example")
        self.play(FadeOut(query_workflow_rep_line_1),
                  FadeIn(query_workflow_rep_line_2),
                  FadeOut(entry_nodes_text_rep),
                  FadeOut(entry_vector_text_rep))
        # BFS traversal
        self.play(*unified_navigating_graph_edges.undo_highlight_nodes(*entry_nodes))
        self.play(*unified_navigating_graph_objects.fadeOut_nodes(all=True))
        all_edges = self.ung_cross_group_edges + self.ung_inner_graph_edges
        bfs_queue = [(vec, None) for vec in entry_vectors]
        visited_edges = set()
        visited_nodes = set()
        visited_vectors = set()
        while len(bfs_queue) != 0:
            print(bfs_queue)
            next_bfs_queue = []
            new_edges = set()
            new_nodes = set()
            new_vectors = set()
            for vec, inEdge in bfs_queue:
                if vec in visited_vectors or vec in new_vectors:
                    continue
                # add vec
                new_vectors.add(vec)
                # add nodes
                node = self.document_to_label_set[vec]
                if node not in visited_nodes:
                    new_nodes.add(node)
                # add edges
                if inEdge is not None and inEdge not in visited_edges:
                    new_edges.add(inEdge)
                # add unexplored edges to the queue
                edges = filter_edges(all_edges, f=[vec])
                for _, t in edges:
                    next_bfs_queue.append((t, (vec, t)))
            anim = []
            all_nodes = new_nodes.union(visited_nodes)
            for node_name in all_nodes:
                node_object = [*unified_navigating_graph_objects.get_objects(node_name)][0]
                if node_name in new_nodes:
                    anim.extend([*node_object.fadeIn_box()])
                new_vectors_for_node = [vec for vec in new_vectors if self.document_to_label_set[vec] == node_name]
                anim.extend([*node_object.fadeIn_nodes(*new_vectors_for_node)])
            anim.extend([*unified_navigating_graph_edges.fadeIn_edges(*new_edges)])
            if len(anim) != 0:
                self.next_slide("Then we traverse...")
                self.play(*anim)
            visited_edges.update(new_edges)
            visited_nodes.update(new_nodes)
            visited_vectors.update(new_vectors)
            bfs_queue = next_bfs_queue

        # clean up
        self.next_slide(notes="")
        self.play(self._set_title("Unified Navigating Graph"),
                  FadeOut(new_query_workflow_rep, query_workflow_rep_line_2),
                  *unified_navigating_graph_objects.fadeOut_nodes(*visited_vectors),
                  *unified_navigating_graph_objects.fadeOut_nodes(*visited_nodes),
                  *unified_navigating_graph_edges.fadeOut_edges(*visited_edges))
        self.play(*unified_navigating_graph_objects.fadeIn_nodes(all=True))
        self.play(*unified_navigating_graph_edges.fadeIn_edges(*self.ung_inner_graph_edges))
        self.play(*unified_navigating_graph_edges.fadeIn_edges(*self.ung_cross_group_edges))

    def construct(self):
        # param = {}
        param = self.section_1()
        param = self.section_2(**param)
        param = self.section_3(**param)
        self.query_example(
            r"$v_{q}$",
            ["venue = SIGMOD", "year = 2025"],
            [1, 4],
            [2, 8],
            param.get("legend", None),
            param.get("unified_navigating_graph_rep", None),
            param.get("unified_navigating_graph_edges", None),
        )


if __name__ == "__main__":
    with tempconfig({"quality": "medium_quality"}):
        scene = LNGDemonstration()
        scene.render()
