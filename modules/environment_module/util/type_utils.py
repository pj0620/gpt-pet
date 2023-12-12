def is_valid_integer(s):
    try:
        int(s)  # Try to convert the string to an integer
        return True
    except ValueError:
        return False
