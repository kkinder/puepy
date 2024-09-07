def node_to_dict(node, remove_ids=False):
    node_dict = {"type": node.nodeName}
    if node.nodeType == node.TEXT_NODE:
        node_dict["text"] = node.nodeValue
    else:
        if node.attributes is not None:
            attrs = {}
            for attr in node.attributes.keys():
                if attr != "id" or not remove_ids:
                    attrs[attr] = node.getAttribute(attr)
            node_dict["attributes"] = attrs

        children = []
        for child in node.childNodes:
            children.append(node_to_dict(child, remove_ids=remove_ids))
        if children:
            node_dict["children"] = children

    return node_dict


def dict_to_node(data, doc):
    if data["type"] == "#text":
        return doc.createTextNode(data.get("text", ""))

    node = doc.createElement(data["type"])

    attrs = data.get("attributes", {})
    for attr_name, attr_value in attrs.items():
        node.setAttribute(attr_name, attr_value)

    for child in data.get("children", []):
        child_node = dict_to_node(child, doc)
        node.appendChild(child_node)

    return node
