import usb.core


def pongo_send_command(command: str):
    """Send command to Pongo device."""
    dev = usb.core.find(idVendor=0x05AC, idProduct=0x4141)
    if dev is None:
        return None
    dev.set_configuration()

    dev.ctrl_transfer(0x21, 4, 0, 0, 0)
    dev.ctrl_transfer(0x21, 3, 0, 0, command + "\n")


def pongo_get_key() -> str:
    """Grab key from Pongo device."""
    dev = usb.core.find(idVendor=0x05AC, idProduct=0x4141)
    if dev is None:
        return None
    dev.set_configuration()
    output = dev.ctrl_transfer(0xA1, 1, 0, 0, 512).tobytes()
    key = output.decode('utf-8').split()[-2]
    return key
