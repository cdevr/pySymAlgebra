import unittest
import simplify

class TestSimplify(unittest.TestCase):
    def test_simplify_trivial(self):
        tests = [
          [['x'], 'x'],
          [['*', 3, 2], 6],
          [['*', '3', '2'], 6],
          [['*', 'x', 1], 'x'],
          [['+', 'x', 0], 'x'],
          # [['-', ['*', 8, 'a'], ['*', 2, 'a']], ['*', 6, 'a']],
        ]

        for [input, want] in tests:
            got = simplify.simplify(input)

            print(f"input: {input} got {got}")
            self.assertEqual(got, want)

    def test_simplify_compile(self):
        tests = [
            ['x', 'x'],
            ['x * 1', 'x'],
            ['x + 0', 'x'],
            ['5*x + 3*x', '8*x'],
        ]

        for [input, want] in tests:
            got = simplify.simplify(simplify.compile(input))

            print(f'{input=} {got=} {want=}')
            self.assertEqual(got, want)

if __name__ == '__main__':
    unittest.main()