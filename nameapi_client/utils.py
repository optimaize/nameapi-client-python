def rename_dict_keys_hook(obj: dict):
    """
    Rename the keys of a dictionary.

    This function recursively traverses the dictionary and renames the keys
    based on the following rules:
    - Keys are split by uppercase letters to create separate words.
    - The words are joined with underscores and converted to lowercase.

    Args:
        obj (dict): The dictionary whose keys will be renamed.

    Returns:
        dict: A new dictionary with the keys renamed according to the rules.
    """
    return _rename_keys(obj)


def _rename_keys(d: dict):
    renamed_d = {}
    for key, value in d.items():
        if isinstance(value, dict):
            renamed_d[_rename_key(key)] = _rename_keys(value)
        else:
            renamed_d[_rename_key(key)] = value
    return renamed_d


def _rename_key(key):
    # Split the key by uppercase letters
    words = []
    current_word = ''
    for char in key:
        if char.isupper():
            if current_word:
                words.append(current_word)
            current_word = char.lower()
        else:
            current_word += char
    if current_word:
        words.append(current_word)
    return '_'.join(words)
