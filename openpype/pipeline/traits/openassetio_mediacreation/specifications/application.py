
"""
Specification definitions in the 'application' namespace.

Specifications for entities that undertake specific functional roles.
"""

# WARNING: This file is auto-generated by openassetio-traitgen, do not edit.

from openassetio.trait import TraitsData


from .. import traits



class WorkfileSpecification:
    """
    The entity is the product of some manual task or process, that often
    defines how to produce or derive other data.

    Common examples are the documents opened, worked on and saved by
    artists using DCC tools to create models/images/etc.
    Usage: entity
    """
    kTraitSet = {
        # 'openassetio-mediacreation:application.Work'
        traits.application.WorkTrait.kId,
        # 'openassetio-mediacreation:content.LocatableContent'
        traits.content.LocatableContentTrait.kId,
        # 'openassetio-mediacreation:usage.Entity'
        traits.usage.EntityTrait.kId,

    }

    def __init__(self, traitsData):
        """
        Constructs the specification as a view on the supplied
        shared @fqref{TraitsData} "TraitsData" instance.

        @param traitsData @fqref{TraitsData} "TraitsData"

        @warning Specifications are always a view on the supplied data,
        which is held by reference. Any changes made to the data will be
        visible to any other specifications or @ref trait "traits" that
        wrap the same TraitsData instance.
        """
        if not isinstance(traitsData, TraitsData):
            raise TypeError("Specifications must be constructed with a TraitsData instance")
        self.__data = traitsData

    def traitsData(self):
        """
        Returns the underlying (shared) @fqref{TraitsData} "TraitsData"
        instance held by this specification.
        """
        return self.__data

    @classmethod
    def create(cls):
        """
        Returns a new instance of the Specification, holding a new
        @fqref{TraitsData} "TraitsData" instance, pre-populated with all
        of the specifications traits.
        """
        data = TraitsData(cls.kTraitSet)
        return cls(data)


    def workTrait(self):
        """
        Returns the view for the 'openassetio-mediacreation:application.Work' trait wrapped around
        the data held in this instance.
        """
        return traits.application.WorkTrait(self.traitsData())

    def locatableContentTrait(self):
        """
        Returns the view for the 'openassetio-mediacreation:content.LocatableContent' trait wrapped around
        the data held in this instance.
        """
        return traits.content.LocatableContentTrait(self.traitsData())

    def entityTrait(self):
        """
        Returns the view for the 'openassetio-mediacreation:usage.Entity' trait wrapped around
        the data held in this instance.
        """
        return traits.usage.EntityTrait(self.traitsData())
