#!/usr/bin/env python
#
# License: BSD
#   https://raw.github.com/stonier/rqt_py_trees/license/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
.. module:: visibility
   :platform: Unix
   :synopsis: Converting back and forth the visibility level formats.

We have a python variable, a ros msg variable, and also the combobox variable!
"""

##############################################################################
# Imports
##############################################################################

import collections
import py_trees
import py_trees_msgs.msg as py_trees_msgs
import uuid_msgs.msg as uuid_msgs
import unique_id

##############################################################################
# Imports
##############################################################################

combo_to_py_trees = collections.OrderedDict([
    ("All", py_trees.common.VisibilityLevel.ALL),
    ("Detail", py_trees.common.VisibilityLevel.DETAIL),
    ("Component", py_trees.common.VisibilityLevel.COMPONENT),
    ("Big Picture", py_trees.common.VisibilityLevel.BIG_PICTURE)]
)

saved_setting_to_combo_index = {
    0: 0,
    1: 1,
    2: 2,
    3: 3
}

msg_to_py_trees = {
    py_trees_msgs.Behaviour.BLACKBOX_LEVEL_DETAIL: py_trees.common.BlackBoxLevel.DETAIL,
    py_trees_msgs.Behaviour.BLACKBOX_LEVEL_COMPONENT: py_trees.common.BlackBoxLevel.COMPONENT,
    py_trees_msgs.Behaviour.BLACKBOX_LEVEL_BIG_PICTURE: py_trees.common.BlackBoxLevel.BIG_PICTURE,
    py_trees_msgs.Behaviour.BLACKBOX_LEVEL_NOT_A_BLACKBOX: py_trees.common.BlackBoxLevel.NOT_A_BLACKBOX
}

items_with_hidden_children = []


def is_root(behaviour_id):
    """
    Check the unique id to determine if it is the root (all zeros).

    :param str behaviour_id:
    """
    return behaviour_id == str(uuid_msgs.UniqueID())


def get_branch_blackbox_level(behaviours, behaviour_id, current_level):
    """
    Computes the critial (minimum) blackbox level present in the branch above
    this behaviour.

    :param {id: py_trees_msgs.Behaviour} behaviours: (sub)tree of all behaviours, including this one
    :param str behaviour_id: id of this behavour
    :param py_trees.common.BlackBoxLevel current_level
    """
    if is_root(behaviour_id):
        return current_level
    parent_id = str(behaviours[behaviour_id].parent_id)
    new_level = min(behaviours[behaviour_id].blackbox_level, current_level)
    return get_branch_blackbox_level(behaviours, parent_id, new_level)

def is_parent_visible(behaviours, behaviour_id):
    """
    :param {id: py_trees_msgs.Behaviour} behaviours:
    :param str behaviour_id:
    """
    parent_id = str(behaviours[behaviour_id].parent_id)
    for i in items_with_hidden_children:
        if i == str(parent_id):
            return False

    if parent_id in behaviours:
        return is_parent_visible(behaviours, parent_id)

    return True

def is_visible(behaviours, behaviour_id, visibility_level):
    """
    :param {id: py_trees_msgs.Behaviour} behaviours:
    :param str behaviour_id:
    :param py_trees.common.VisibilityLevel visibility_level
    """
    # check if the parent is visible
    if not is_parent_visible(behaviours, behaviour_id):
        return False

    branch_blackbox_level = get_branch_blackbox_level(
        behaviours,
        str(behaviours[behaviour_id].parent_id),
        py_trees.common.BlackBoxLevel.NOT_A_BLACKBOX
    )
    # see also py_trees.display.generate_pydot_graph
    return visibility_level < branch_blackbox_level


def filter_behaviours_by_visibility_level(behaviours, visibility_level):
    """
    Drops any behaviours whose blackbox level does not match the required visibility
    level. See the py_trees.common module for more information.

    :param py_trees_msgs.msg.Behaviour[] behaviours
    :returns: py_trees_msgs.msg.Behaviour[]
    """
    behaviours_by_id = {str(b.own_id): b for b in behaviours}
    visible_behaviours = [b for b in behaviours if is_visible(behaviours_by_id,
                                                              str(b.own_id),
                                                              visibility_level)
                          ]
    return visible_behaviours
