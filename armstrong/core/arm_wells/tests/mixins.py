from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from ..models import Well, WellType, Node

from ._utils import TestCase, \
                    generate_random_well, \
                    generate_random_welltype, \
                    generate_random_story

from .arm_wells_support.models import MissingFieldWell, MissingFieldWellNode, \
                                      NewWell, NewNode, \
                                      DifferentWell, DifferentWellType, \
                                      WrongRelationWell, WrongRelationNode


class WellMixinTestCase(TestCase):
    def test_missing_type_field(self):
        well = MissingFieldWell()
        with self.assertRaises(NotImplementedError):
            well.type

        well = MissingFieldWell.objects.create()
        with self.assertRaises(NotImplementedError):
            well.type

    def test_has_type_field(self):
        well = Well()
        with self.assertRaises(ObjectDoesNotExist):
            well.type

        with self.assertRaises(IntegrityError):
            Well.objects.create()

        well = Well.objects.create(type=generate_random_welltype())
        self.assertEqual(WellType, type(well.type))


class WellNodeMixinTestCase(TestCase):
    def test_missing_well_field(self):
        node = MissingFieldWellNode()
        with self.assertRaises(NotImplementedError):
            node.well

        with self.assertRaises(IntegrityError):
            MissingFieldWellNode.objects.create()

    def test_has_well_field(self):
        node = Node()
        with self.assertRaises(ObjectDoesNotExist):
            node.well

        with self.assertRaises(IntegrityError):
            Node.objects.create(content_object=generate_random_story(),
                                order=100)

        node = Node.objects.create(content_object=generate_random_story(),
                                   well=generate_random_well(),
                                   order=100)
        self.assertEqual(Well, type(node.well))


class SubclassesTestCase(TestCase):
    def setUp(self):
        self.well = NewWell.objects.create(type=generate_random_welltype())
        self.node1 = NewNode.objects.create(content_object=generate_random_story(),
                                            well=self.well,
                                            order=100)

        self.node2 = NewNode.objects.create(content_object=generate_random_story(),
                                            well=self.well,
                                            order=9)

    def test_relations(self):
        self.assertEqual(WellType, type(self.well.type))
        self.assertEqual(NewWell, type(self.node1.well))
        self.assertEqual(NewWell, type(self.node2.well))
        self.assertEqual(NewNode, type(self.node1))
        self.assertEqual(NewNode, type(self.node2))

    def test_wrong_relation(self):
        dwt = DifferentWellType.objects.create(title="title", slug="slug")
        dw = DifferentWell.objects.create(type=dwt)
        self.assertEqual(DifferentWellType, type(dw.type))

        with self.assertRaises(ValueError):
            # NewNode relates to NewWell
            NewNode.objects.create(
                content_object=generate_random_story(),
                well=generate_random_well(),
                order=1
            )
        with self.assertRaises(ValueError):
            # DifferentWell relates to DifferentWellType
            DifferentWell.objects.create(type=generate_random_welltype())

    def test_items_relation(self):
        # make sure 'items' works
        self.assertEqual(2, self.well.items.count())

        # make sure related_name 'nodes' works
        self.assertEqual(self.well.items.count(),
                         self.well.nodes.count())

        # make sure content is the same
        self.assertEqual(self.well.nodes.all()[0], self.node2)
        self.assertEqual(self.well.nodes.all()[1], self.node1)
        self.assertEqual(self.well.items[0],
                         self.well.nodes.all()[0].content_object)
        self.assertEqual(self.well.items[1],
                         self.well.nodes.all()[1].content_object)

    def test_items_wrong_relation(self):
        well = WrongRelationWell.objects.create(type=generate_random_welltype())
        node = WrongRelationNode.objects.create(
                content_object=generate_random_story(),
                well=well,
                order=1
            )

        with self.assertRaises(AttributeError):
            well.items
        with self.assertRaises(AttributeError):
            well.nodes

        self.assertEqual(1, well.foo.count())
        self.assertEqual(node, well.foo.all()[0])
