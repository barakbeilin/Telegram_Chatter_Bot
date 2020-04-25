from src import common_utils


def test_one_to_one_dict():

    a = common_utils.one_to_one_dict()
    a.add_item("foo", 1)
    a.add_item("bar", 2)

    print(a.get_all_rights())
    print(a.get_all_lefts())
    print("foo" in a.get_all_lefts())
    print(1 in a.get_all_rights())

    print("a.get_value_by_key(1)=" + str(a.get_value_by_key(1)))
    print("a.get_value_by_key('foo')="+str(a.get_value_by_key("foo")))

    a.remove_item(left="foo")
    print(a.get_all_rights())
    print(a.get_all_lefts())
    print("foo" in a.get_all_lefts())


if __name__ == "__main__":
    test_one_to_one_dict()
