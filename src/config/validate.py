import yamale

from logs.log_handler import logger


def validate_yaml_file(schema: str, config: str) -> bool:
    """
    Validate a YAML file against a given schema.

    Parameters:
    schema (str): The file path to the schema YAML.
    config (str): The file path to the config YAML.

    Returns:
    bool: True if the YAML is valid, False otherwise.
    """
    try:
        from yamale import YamaleError
    except ImportError:
        logger.error("Unable to import YamaleError. Please install the yamale package.")
        return False

    schema = yamale.make_schema(schema)
    config = yamale.make_data(config)

    try:
        yamale.validate(schema, config)
    except YamaleError as exception:
        log_validation_errors(exception)
        return False

    # logger.info("The YAML file is valid!")
    return True


def log_validation_errors(exception: yamale.YamaleError) -> None:
    """
    Log errors from YAML validation.

    Parameters:
    exception (YamaleError): The exception raised from Yamale.

    """
    logger.error("Validation failed!")
    for result in exception.results:
        logger.error("Error validating data '%s' with '%s'", result.data, result.schema)
        for error in result.errors:
            logger.error("%s", error)
