import re

from maya import cmds

import pyblish.api


class CollectAssData(pyblish.api.InstancePlugin):
    """Collect Ass data."""

    # Offset to be after renderable camera collection.
    order = pyblish.api.CollectorOrder + 0.2
    label = 'Collect Ass'
    families = ["ass"]

    def process(self, instance):
        objsets = instance.data['setMembers']

        for objset in objsets:
            objset = str(objset)
            members = cmds.sets(objset, query=True)
            if members is None:
                self.log.warning("Skipped empty instance: \"%s\" " % objset)
                continue
            if "content_SET" in objset:
                instance.data['setMembers'] = members
                self.log.debug('content members: {}'.format(members))
            elif objset.startswith("proxy_SET"):
                msg = "You have multiple proxy meshes, please only use one"
                assert len(members) == 1, msg
                instance.data['proxy'] = members
                self.log.debug('proxy members: {}'.format(members))

        # Indicate to user that it'll be a single frame.
        sequence = instance.data.get("exportSequence", False)
        if not sequence:
            group = re.compile(r" \[.*\]")
            instance.data["label"] = group.sub("", instance.data["label"])

        # Use camera in object set if present else default to render globals
        # camera.
        cameras = cmds.ls(type="camera", long=True)
        renderable = [c for c in cameras if cmds.getAttr("%s.renderable" % c)]
        camera = renderable[0]
        for node in instance.data["setMembers"]:
            camera_shapes = cmds.listRelatives(
                node, shapes=True, type="camera"
            )
            if camera_shapes:
                camera = node
        instance.data["camera"] = camera

        self.log.debug("data: {}".format(instance.data))
