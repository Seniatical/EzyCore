## Crucial tests for main 
from ezycore import Manager, Segment
from ezycore.models import Model, Config
from ezycore.exceptions import SegmentError
from typing import Union
import unittest


class BasicTestModel(Model):
    field_1: str
    field_2: int
    field_3: bool
    field_4: Union[int, float]

    _config: Config = {'search_by': 'field_2'}


class TestManager(unittest.TestCase):
    def test_segments(self):
        seg = Segment(name='Foo', model=BasicTestModel)

        self.assertEqual((seg.name, seg.model, seg.max_size, seg.make_space), ('Foo', BasicTestModel, 1000, True), 'Creating basic segment failed')

        try:
            Segment('Foo', None)
            Segment(10, 'NoModel')
            Segment('Foo', 20)
            Segment('Foo', BasicTestModel, max_size='NoInt')
            Segment('Foo', BasicTestModel, max_size='NotSure')
            
            self.fail('Parameter verification failed')
        except SegmentError:
            self.assertEqual(0, 0)

    def test_basic_use(self):
        manager = Manager(locations=['test'], models={'test': BasicTestModel})

        self.assertEqual(tuple(i.name for i in manager.segments()), ('test',), 'Creating manager segments failed')
        seg = Segment('Foo', BasicTestModel)

        manager.add_segment(seg)
        self.assertEqual(tuple(i.name for i in manager.segments()), ('test', 'Foo'), 'Adding segments failed')

        manager.update_segment('Foo', name='Bar')
        self.assertEqual(tuple(i.name for i in manager.segments()), ('test', 'Bar'), 'Editting segments failed')

        s = manager.remove_segment('Bar')
        self.assertEqual(tuple(i.name for i in manager.segments()), ('test',), 'Deleting segments failed')

        self.assertEqual(s._get_manager(), None, 'Manager exists on independant segment')
