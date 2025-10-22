import os
import logging

logger = logging.getLogger(__name__)


def validate_args(args):
    path = args.path
    prompt = args.prompt

    # Validate that either path is provided or prompt is True, but not both
    if path is None and not prompt:
        raise ValueError(
            "Either --path must be provided or --prompt must be set to True."
        )
    if path is not None and prompt:
        raise ValueError("Cannot use --path and --prompt together.")

    # If path is provided, check if the file exists
    if path is not None and not os.path.isfile(path):
        raise FileNotFoundError(f"The file at path '{path}' does not exist.")

    logger.info("All checks passed!")
