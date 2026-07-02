from enum import Enum


class Category(str, Enum):
    """Ticket category taxonomy. Must match docs/01_architecture/DATA_MODEL.md Section 2 exactly."""

    SETUP_INSTALLATION = "Setup / Installation"
    WIFI_NETWORK = "Wi-Fi / Network Connectivity"
    BLUETOOTH_PAIRING = "Bluetooth / Pairing"
    FIRMWARE_UPDATE = "Firmware Update"
    SOUND_QUALITY = "Sound Quality / Distortion"
    AMP_SPEAKER_COMPATIBILITY = "Amplifier / Speaker Compatibility"
    SUBWOOFER_SETUP = "Subwoofer Setup"
    PRODUCT_DEFECT = "Product Defect / Hardware Issue"
    SHIPPING_DAMAGED = "Shipping / Damaged Delivery"
    RETURNS_REFUNDS = "Returns / Refunds"
    WARRANTY_REGISTRATION = "Warranty / Registration"
    ORDER_ACCOUNT_BILLING = "Order / Account / Billing"
    GENERAL_QUESTION = "General Product Question"


class Priority(str, Enum):
    """Deterministic priority levels. Must match docs/01_architecture/DATA_MODEL.md Section 3 exactly."""

    URGENT = "Urgent"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
