import maya.cmds as cmds

import pyblish.api


class ValidateXgen(pyblish.api.InstancePlugin):
    """Validate Xgen data."""

    label = "Validate Xgen"
    order = pyblish.api.ValidatorOrder
    host = ["maya"]
    families = ["xgen"]

    def process(self, instance):
        # Validate only xgen collections are in objectset.
        nodes = (
            instance.data["xgenNodes"] +
            cmds.ls(instance, type="transform", long=True)
        )
        remainder_nodes = []
        for node in instance:
            if node in nodes:
                continue
            remainder_nodes.append(node)

        msg = "Invalid nodes in the objectset:\n{}".format(remainder_nodes)
        assert not remainder_nodes, msg
