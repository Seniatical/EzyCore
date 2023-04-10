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


class AlternateTestModel(Model):
    field_1: int

    _config: Config = {'search_by': 'field_1'}


class TestManager(unittest.TestCase):
    def setUp(self) -> None:
        self.manager = Manager(locations=['test'], models={'test': BasicTestModel})

    def test_segment_creation(self):
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
            pass

    def test_basic_use(self):
        manager = self.manager

        self.assertEqual(tuple(i.name for i in manager.segments()), ('test',), 'Creating manager segments failed')
        seg = Segment('Foo', BasicTestModel)

        manager.add_segment(seg)
        self.assertEqual(tuple(i.name for i in manager.segments()), ('test', 'Foo'), 'Adding segments failed')

        manager.update_segment('Foo', name='Bar')
        self.assertEqual(tuple(i.name for i in manager.segments()), ('test', 'Bar'), 'Editting segments failed')

        s = manager.remove_segment('Bar')
        self.assertEqual(tuple(i.name for i in manager.segments()), ('test',), 'Deleting segments failed')

        self.assertEqual(s._get_manager(), None, 'Manager exists on independant segment')

    def test_models(self):
        manager = self.manager
        
        self.assertEqual(tuple(i.__name__ for i in manager.models()), ('BasicTestModel',), 'Manager failed adding model')
        manager.update_segment('test', model=AlternateTestModel)

        self.assertEqual(tuple(i.__name__ for i in manager.models()), ('AlternateTestModel',), 'Manager failed adding model')
        self.assertEqual(manager._modify_mod()['test'], AlternateTestModel)

        seg = manager.get_segment('test')
        seg.update_segment(model=BasicTestModel)

        self.assertEqual(tuple(i.__name__ for i in manager.models()), ('BasicTestModel',), 'Manager failed adding model')

    def test_methods(self):
        ## Dict methods
        test = self.manager['test']
        self.assertEqual(test, self.manager.get_segment('test'), 'Failed __getitem__')

        try:
            self.manager['test'] = 'Bar'
            return self.fail('Failed __setitem__, invalid segment created')
        except TypeError:
            self.manager['test'] = Segment('Bar', model=BasicTestModel)

        self.assertEqual(self.manager.get_segment('Bar').name, 'Bar', 'Failed __setitem__')

        del self.manager['Bar']
        self.assertEqual(tuple(i for i in self.manager.models()), tuple(), 'Failed __delitem__')

        self.manager.add_segment('test', model=BasicTestModel)

        ## Iterations
        self.assertEqual(self.manager, iter(self.manager))

        d = []
        for seg in self.manager:
            d.append(seg.name)
        self.assertEqual(tuple(d), tuple(i.name for i in self.manager.segments()), 'Failed __next__')

        ## Contains
        try:
            seg in self.manager
            self.fail('Failed __contains__, invalid comparison made')
        except AssertionError:
            pass
        self.assertTrue('test' in self.manager, 'Failed __contains__')

        ## Enter exit
        with self.manager as M:
            self.assertEqual(M, self.manager, 'Failed __enter__')
