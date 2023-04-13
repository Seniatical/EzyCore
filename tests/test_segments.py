from ezycore import Segment
from ezycore.models import Model, Config
from pydantic import ValidationError
import unittest

class BasicTestModel(Model):
    field_1: str
    field_2: int
    field_3: bool

    _config: Config = {'search_by': 'field_2'}


class TestSegments(unittest.TestCase):
    def setUp(self) -> None:
        self.segment = Segment(name='Test', model=BasicTestModel, max_size=10)

    def tearDown(self) -> None:
        self.segment.clear()

    ## TESTS

    def test_segment_add(self):
        data = dict(field_1='Foo', field_2=10, field_3=False)
        self.segment.add(data)
        self.assertEqual(self.segment.get(10, '*'), data)

        try:
            self.segment.add(data)

            return self.fail('Duplicate key added')
        except ValueError:
            pass

    def test_segment_get(self):
        data = dict(field_1='Foo', field_2=10, field_3=False)
        self.segment.add(data)

        self.assertEqual(self.segment.get(10, '*'), data)
        self.assertEqual(self.segment.get(10, 'field_1')['field_1'], 'Foo')
        self.assertEqual(self.segment.get(-1, default=None), None)
        self.assertEqual(self.segment.get(10), BasicTestModel(**data))

    def test_segment_delete(self):
        data = dict(field_1='Foo', field_2=10, field_3=False)
        self.segment.add(data)

        try:
            self.segment.remove(-1)

            self.fail('Segment.remove removing invalid values')
        except ValueError:
            pass
        d = self.segment.remove(-1, None)
        self.assertEqual(d, None)

        f = self.segment.remove(10)
        self.assertEqual(f, BasicTestModel(**data).dict())

    def test_segment_edit(self):
        data = dict(field_1='Foo', field_2=10, field_3=False)
        self.segment.add(data)

        self.segment.update(10, field_1='Bar')
        self.assertEqual(self.segment.get(10).field_1, 'Bar')

        try:
            self.segment.update(10, field_3='Nope')

            self.fail('Update field verification failed!')
        except ValidationError:
            pass

    def test_segment_searches(self):
        d1 = dict(field_1='Foo', field_2=10, field_3=False)
        d2 = dict(field_1='Bar', field_2=5, field_3=True)
        d3 = dict(field_1='Foo', field_2=50, field_3=True)

        self.segment.add(d1)
        self.segment.add(d2)
        self.segment.add(d3)

        self.assertEqual(
            self.segment.search(lambda m: m.field_1 == 'Foo', 'field_2'),
            [{'field_2': 50}, {'field_2': 10}], 'Failed search method')

        self.assertEqual(
            self.segment.search_using_re('^Bar$', 'field_2', key='field_1'),
            [{'field_2': 5}], 'Failed regex search'
        )

    def test_segment_cache_invalidation(self):
        for i in range(10):
            self.segment.add(dict(field_1='Foo', field_2=i, field_3=False))
        self.assertEqual(self.segment.last().field_2, 0)
        self.assertEqual(self.segment.first().field_2, 9)

        self.segment.add(dict(field_1='Foo', field_2=10, field_3=False))
        self.assertEqual(self.segment.last().field_2, 1)
        self.assertEqual(self.segment.first().field_2, 10)
