import warnings

warnings.filterwarnings(
    "ignore",
    message=r"The log with transaction hash.*MismatchedABI",
    category=UserWarning,
    module=r"eth_utils\.functional"
)