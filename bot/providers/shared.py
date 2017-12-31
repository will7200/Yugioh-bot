HIGH_CORR = 3
LOW_CORR = 2
battlemode = "NPC Battle Mode,Points: (%d,%d) at location: (%d), message: %s"
current_version = "v2"
nox_current_version = current_version

def look_up_translation_correlation(corr):
    messages = {
        str(HIGH_CORR): 'HIGH',
        str(LOW_CORR): 'LOW'
    }
    return messages.get(str(corr), "UNKNOWN")
