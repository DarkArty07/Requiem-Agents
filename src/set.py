class Set:
    """A custom Set implementation using a list as backing storage.
    Does NOT use Python's built-in set type.
    """

    def __init__(self):
        self._elements = []

    def add(self, element):
        """Adds an element to the set if not already present."""
        if not self.contains(element):
            self._elements.append(element)

    def remove(self, element):
        """Removes an element from the set if present. Raises KeyError if not found."""
        if not self.contains(element):
            raise KeyError(f"Element {element!r} not found in set")
        # Create a new list without the element
        new_elements = []
        for e in self._elements:
            if e != element:
                new_elements.append(e)
        self._elements = new_elements

    def contains(self, element):
        """Returns True if the element is in the set, False otherwise."""
        for e in self._elements:
            if e == element:
                return True
        return False

    def size(self):
        """Returns the number of elements in the set."""
        return len(self._elements)

    def union(self, other_set):
        """Returns a new Set containing elements from both sets."""
        result = Set()
        # Add all elements from this set
        for e in self._elements:
            result.add(e)
        # Add all elements from the other set
        for e in other_set._elements:
            result.add(e)
        return result

    def intersection(self, other_set):
        """Returns a new Set containing only elements present in both sets."""
        result = Set()
        for e in self._elements:
            if other_set.contains(e):
                result.add(e)
        return result

    def __repr__(self):
        return f"Set({self._elements!r})"
