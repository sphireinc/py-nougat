def nougat(data, *keys, default=None):
    result = data
    for i, key in enumerate(keys):
        if not hasattr(result, 'get'):
            return default
        
        if i == len(keys) - 1:
            return result.get(key, default)
        
        result = result.get(key, {})
    
    return result
