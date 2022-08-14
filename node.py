# node utilities

class NODE:
  @staticmethod
  def splay(node, tags: list):
    """
    takes a node like

    example
    - foo: foo_value
    - bar: bar_value

    and returns a objet with result.foo = "foo_value" and result.bar = "bar_value"

    ASSUMPTIONS:
    - that every child is prefixed with a tag and then a colon with a space, like `tag: <value>`
    - that @param `tags` contains each of the tags that are used,
      - e.g. ['foo', 'bar'] for the example above
    - the value of the tags may not be anything but strings, thus the node must be one layer deep
      - i.e. the children may not have children
    """
    result = dict()

    if len(node['children']) != len(tags):
      ABORT(f"ERROR: tag count doesn't match child count:\n tags = '{tags}'\n children = '{node['children']}'")

    for tag, child in zip(tags, node['children']):
      child_value = child['value']
      tag_prefix = tag + ": "

      if not child_value.startswith(tag_prefix):
        ABORT("ERROR: mismatched tag on destructure")

      result[tag] = child_value.removeprefix(tag_prefix)

    return SimpleNamespace(**result)
