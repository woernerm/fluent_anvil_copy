import anvil.server
class TestCase:
    def assertEqual(self, first, second):
        if not first == second:
            raise Exception(f"{first} does not equal {second}")

    def assertLess(self, first, second):
        if not first < second:
            raise Exception(f"{first} is not less than {second}")