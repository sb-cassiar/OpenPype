
"""
Trait definitions in the 'managementPolicy' namespace.

Traits used in a Manager's managementPolicy response.
"""

# WARNING: This file is auto-generated by openassetio-traitgen, do not edit.

from typing import Union

from openassetio.trait import TraitsData


class ManagedTrait:
    """
    A trait indicating that the data matching the supplied trait set is
    handled by the manager.

    There are three possible policies determined by applying/querying
    this trait: * If the response is not imbued with this trait, then
    the
      Manager has no interest in participating in the management of
      entities that match the queried trait set, for either read or
      write.
    * If the response is imbued with this trait, but the "exclusive"
      property is not set, or set to False, then the Manager would
        like the opportunity to manage the data, but the user should
        still be presented with standard Host UI for the type as an
        option.
      * If the "exclusive" property is set to true, then the Manager
        takes exclusive control over data with the queried trait set,
        and any standard host interfaces etc should be suppressed.
    Usage: managementPolicy
    """
    kId = "openassetio-mediacreation:managementPolicy.Managed"

    def __init__(self, traitsData):
        """
        Construct this trait view, wrapping the given data.

        @param traitsData @fqref{TraitsData}} "TraitsData" The target
        data that holds/will hold the traits properties.
        """
        self.__data = traitsData

    def isImbued(self):
        """
        Checks whether the data this trait has been applied to
        actually has this trait.
        @return `True` if the underlying data has this trait, `False`
        otherwise.
        """
        return self.isImbuedTo(self.__data)

    @classmethod
    def isImbuedTo(cls, traitsData):
        """
        Checks whether the given data actually has this trait.
        @param traitsData: Data to check for trait.
        @return `True` if the underlying data has this trait, `False`
        otherwise.
        """
        return traitsData.hasTrait(cls.kId)

    def imbue(self):
        """
        Adds this trait to the held data.

        If the data already has this trait, it is a no-op.
        """
        self.__data.addTrait(self.kId)

    @classmethod
    def imbueTo(cls, traitsData):
        """
        Adds this trait to the provided data.

        If the data already has this trait, it is a no-op.
        """
        traitsData.addTrait(cls.kId)


    def setExclusive(self, exclusive: bool):
        """
        Sets the exclusive property.

        Determines if the manager exclusively handles data matching the
        supplied trait set.

        If True, then standard host controls should be disabled in
        favour of manager delegated UI. For example, file system
        browsers when determining where to load/save data.

        If False, then standard host controls can be presented in
        addition to any custom manager UI.
        """
        if not isinstance(exclusive, bool):
            raise TypeError("exclusive must be a 'bool'.")
        self.__data.setTraitProperty(self.kId, "exclusive", exclusive)

    def getExclusive(self, defaultValue: bool=None) -> Union[bool, None]:
        """
        Gets the value of the exclusive property or the supplied default.

        Determines if the manager exclusively handles data matching the
        supplied trait set.

        If True, then standard host controls should be disabled in
        favour of manager delegated UI. For example, file system
        browsers when determining where to load/save data.

        If False, then standard host controls can be presented in
        addition to any custom manager UI.
        """
        value = self.__data.getTraitProperty(self.kId, "exclusive")
        if value is None:
            return defaultValue

        if not isinstance(value, bool):
            if defaultValue is None:
                raise TypeError(f"Invalid stored value type: '{type(value).__name__}' should be 'bool'.")
            return defaultValue
        return value
