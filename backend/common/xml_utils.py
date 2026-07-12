def xml_to_dict(element):
    """
    Converts an lxml.etree element into a python dictionary,
    preserving attributes and handling list child nodes cleanly.
    """
    # If the element has no children
    if len(element) == 0:
        val = element.text
        if val is not None:
            val = val.strip()
            # Convert simple types
            if val.lower() == 'true':
                val = True
            elif val.lower() == 'false':
                val = False
            elif val == '':
                val = None
        
        # If it has attributes but no children, merge attributes and text
        if element.attrib:
            attribs = {}
            for k, v in element.attrib.items():
                if v.lower() == 'true':
                    attribs[k] = True
                elif v.lower() == 'false':
                    attribs[k] = False
                else:
                    attribs[k] = v
            if val is not None:
                attribs['value'] = val
            return attribs
            
        # Empty elements like <department_id/> without text or attributes become None
        if val is None and not element.attrib:
            return None
            
        return val

    # If the element has children
    result = {}
    
    # If this is a known list container (like custom_fields) or its children all have same tag,
    # return it directly as a list to avoid nested dicts like {'field': [...]}.
    if element.tag == 'custom_fields':
        return [xml_to_dict(c) for c in element]
    
    children_by_tag = {}
    for child in element:
        children_by_tag.setdefault(child.tag, []).append(child)
        
    for tag, children in children_by_tag.items():
        is_list = len(children) > 1 or tag == 'field'
        
        parsed_children = [xml_to_dict(c) for c in children]
        if is_list:
            result[tag] = parsed_children
        else:
            result[tag] = parsed_children[0]
            
    # Include attributes of this element if any
    if element.attrib:
        for k, v in element.attrib.items():
            if v.lower() == 'true':
                result[k] = True
            elif v.lower() == 'false':
                result[k] = False
            else:
                result[k] = v
                
    return result
