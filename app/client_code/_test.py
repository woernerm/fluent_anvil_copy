import anvil.server
class TestCase:
    @classmethod
    def assertEqual(cls, first, second):
        if not first == second:
            raise Exception(f"{first} does not equal {second}")

    @classmethod
    def assertTrue(cls, condition):
        if not bool(condition):
            raise Exception(f"{condition} is not True.")

    @classmethod
    def assertFalse(cls, condition):
        if bool(condition):
            raise Exception(f"{condition} is not False.")

    @classmethod
    def assertLess(cls, first, second):
        if not first < second:
            raise Exception(f"{first} is not less than {second}")