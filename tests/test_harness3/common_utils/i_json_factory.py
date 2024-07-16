"""Interface for a factory that creates needed JSON test data."""

import abc


class IJsonFactory(abc.ABC):
    """Interface for a factory that creates needed JSON test data.

    Extend this abstract class and implement the methods to retrieve/
    generate the given JSON test data, which are the inputs for the commands
    Configure, AssignResources and Scan.
    """

    # To implement with create_subarray_configuration
    # and with get_subarray_input_json
    # (sometimes called as prepare_json_args_for_commands)
    @abc.abstractmethod
    def create_subarray_configure_command_input(self) -> str:
        """Create the JSON input for the Configure command.

        :returns: The JSON input for the Configure command.
        """
        pass

    @abc.abstractmethod
    def create_subarray_scan_command_input(self) -> str:
        """Create the JSON input for the Scan command.

        :returns: The JSON input for the Scan command.
        """
        pass

    # To implement with create_assign_resources_configuration
    # and with get_subarray_input_json

    @abc.abstractmethod
    def create_subarray_assign_resources_command_input(self) -> str:
        """Create the JSON input for the AssignResources command.

        :returns: The JSON input for the AssignResources command.
        """
        pass

    # To implement with create_centralnode_configuration
    # and with get_centralnode_input_json
    # (sometimes called also as prepare_json_args_for_centralnode_commands)

    @abc.abstractmethod
    def create_central_node_assign_resources_command_input(self) -> str:
        """Create the JSON input for the ReleaseResources command.

        :returns: The JSON input for the ReleaseResources command.
        """
        pass

    @abc.abstractmethod
    def create_central_node_release_resources_command_input(self) -> str:
        """Create the JSON input for the ReleaseResources command.

        :returns: The JSON input for the ReleaseResources command.
        """
        pass

    # Others

    @abc.abstractmethod
    def create_default_vcc_config_command_input(self) -> str:
        """Create the JSON input for the default VCC configuration.

        :returns: The JSON input for the default VCC configuration.
        """
        pass
