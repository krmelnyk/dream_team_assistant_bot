"""Domain-specific exceptions (skeleton)."""


ERROR_PREFIX = "[ERROR] "


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as error:
            return f"{ERROR_PREFIX}{error}"
        except KeyError:
            return f"{ERROR_PREFIX}Contact not found"
        except IndexError:
            return f"{ERROR_PREFIX}Enter the required arguments for the command"
    return inner
