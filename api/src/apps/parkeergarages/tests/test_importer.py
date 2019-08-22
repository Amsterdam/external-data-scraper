from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from apps.parkeergarages.models import (GuidanceSign, GuidanceSignSnapshot,
                                        ParkingGuidanceDisplay,
                                        ParkingLocation,
                                        ParkingLocationSnapshot)


class TestParkingLocationImporter(TestCase):
    fixtures = ['parkeergarages.json']

    def test_ok(self):
        call_command('import_parkinglocation')
        self.assertEqual(ParkingLocation.objects.count(), 3)

        parkinglocation = ParkingLocation.objects.filter(id=1)[0]
        self.assertEqual(parkinglocation.name, 'CE-P28 PTA Touringcars')
        self.assertEqual(parkinglocation.long_capacity, None)
        self.assertEqual(parkinglocation.short_capacity, 42)
        self.assertEqual(parkinglocation.free_space_short, 0)
        self.assertEqual(parkinglocation.free_space_long, None)
        self.assertEqual(parkinglocation.geometrie.srid, 4326)

    def test_iterate_raw_model(self):
        iterator = ParkingLocationSnapshot.objects.limit_offset_iterator(1)

        self.assertEqual(next(iterator), ParkingLocationSnapshot.objects.get(id=1))
        self.assertEqual(next(iterator), ParkingLocationSnapshot.objects.get(id=2))

        with self.assertRaises(StopIteration):
            self.assertIsNone(next(iterator))

    def test_only_latest(self):
        call_command('import_parkinglocation')
        self.assertEqual(ParkingLocation.objects.count(), 3)

        hour_later = timezone.now() + timezone.timedelta(hours=1)
        ParkingLocationSnapshot.objects.filter(pk=1).update(scraped_at=hour_later)

        call_command('import_parkinglocation')
        self.assertEqual(ParkingLocation.objects.count(), 5)


class TestGuidanceSignImporter(TestCase):
    fixtures = ['parkeergarages.json']

    def test_ok(self):
        call_command('import_guidancesign')
        self.assertEqual(GuidanceSign.objects.count(), 3)
        self.assertEqual(ParkingGuidanceDisplay.objects.count(), 7)

        guidancesign = GuidanceSign.objects.order_by('id').first()
        self.assertEqual(guidancesign.name, 'FJ462B13 - ZO-B13 Burg.Stramanweg 02510/080')
        self.assertEqual(guidancesign.state, 'ok')
        self.assertEqual(guidancesign.type, 'guidancesign')
        self.assertEqual(guidancesign.geometrie.srid, 4326)

        parkingguidancedisplay = ParkingGuidanceDisplay.objects.order_by('id').first()
        self.assertEqual(parkingguidancedisplay.output, 'X')

    def test_iterate_raw_model(self):
        iterator = GuidanceSignSnapshot.objects.limit_offset_iterator(1)

        self.assertEqual(next(iterator), GuidanceSignSnapshot.objects.get(id=1))
        self.assertEqual(next(iterator), GuidanceSignSnapshot.objects.get(id=2))

        with self.assertRaises(StopIteration):
            self.assertIsNone(next(iterator))

    def test_guidance_sign_ignored(self):
        call_command('import_guidancesign')
        self.assertEqual(GuidanceSign.objects.count(), 3)

        hour_later = timezone.now() + timezone.timedelta(hours=1)
        GuidanceSignSnapshot.objects.filter(id=1).update(scraped_at=hour_later)

        call_command('import_guidancesign')
        self.assertEqual(GuidanceSign.objects.count(), 3)

    def test_only_latest(self):
        call_command('import_guidancesign')
        self.assertEqual(ParkingGuidanceDisplay.objects.count(), 7)

        hour_later = timezone.now() + timezone.timedelta(hours=1)
        GuidanceSignSnapshot.objects.filter(pk=1).update(scraped_at=hour_later)

        call_command('import_guidancesign')
        self.assertEqual(ParkingGuidanceDisplay.objects.count(), 11)
