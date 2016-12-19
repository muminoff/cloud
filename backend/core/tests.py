# Django
from django.test import TestCase
from django.contrib.auth.models import User

# Core
from core.models import Profile


class MainTestCase(TestCase):
    fixtures = ['fixtures/services.yaml']

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='qwe123123',
            email='testuser@localhost')

    def tearDown(self):
        del self.user

    def test_user_name(self):
        self.assertEqual(self.user.username, 'testuser')

    def test_user_email(self):
        self.assertEqual(self.user.email, 'testuser@localhost')

    def test_user_password(self):
        self.assertTrue(self.user.check_password('qwe123123'))
        self.assertFalse(self.user.check_password('wrong password'))

    def test_user_profile_presence(self):
        self.assertIsNotNone(self.user.profile)

    def test_user_profile_instance(self):
        from core.models import Profile
        self.assertIsInstance(self.user.profile, Profile)

    def test_user_profile_service(self):
        from core.models import Service, CAPACITY_CHOICES
        self.assertIsInstance(self.user.profile.service, Service)
        self.assertEqual(self.user.profile.service.capacity, CAPACITY_CHOICES[0][0])

    def test_user_profile_language(self):
        from django.conf import settings
        self.assertEqual(self.user.profile.language, settings.LANGUAGE_CODE)

    def test_user_profile_storage(self):
        self.assertEqual(self.user.profile.storage_set.first().storage_type, 1)
        self.assertEqual(self.user.profile.storage_set.last().storage_type, 2)

    def test_directories_and_files(self):
        from core.models import DirMeta, FileMeta

        # Create first directory
        self.user.profile.storage_set.first().create_directory(parent=None, name='root-directory')
        root_directory = DirMeta.objects.get(name='root-directory')
        self.assertIsNotNone(root_directory)
        self.assertIsInstance(root_directory, DirMeta)
        self.assertEqual(root_directory.name, 'root-directory')
        self.assertFalse(root_directory.has_parent)
        self.assertTrue(root_directory.is_empty)

        # Create second directory into first directory
        self.user.profile.storage_set.first().create_directory(parent=root_directory, name='child-directory')
        child_directory = DirMeta.objects.get(name='child-directory')
        self.assertIsNotNone(child_directory)
        self.assertIsInstance(child_directory, DirMeta)
        self.assertEqual(child_directory.name, 'child-directory')
        self.assertTrue(child_directory.has_parent)
        self.assertTrue(child_directory.is_empty)

        # Create ten files into first root directory
        for x in range(1, 11):
            self.user.profile.storage_set.first().create_file(
                parent=root_directory,
                name='test-file-' + str(x),
                content_type='text',
                size=10 * x)

        # All files should be in root directory
        for filemetaobject in FileMeta.objects.filter(parent=root_directory):
            self.assertIn(filemetaobject, self.user.profile.storage_set.first().browse(parent=root_directory))

        # Get directories
        self.assertIn(child_directory, self.user.profile.storage_set.first().browse(parent=root_directory))

        # Create fifty directories into second child directory
        for x in range(1, 51):
            self.user.profile.storage_set.first().create_directory(
                parent=root_directory,
                name='test-directory' + str(x))

        # All directories should be in second child directory
        for directorymetaobject in DirMeta.objects.filter(parent=child_directory):
            self.assertIn(directorymetaobject, self.user.profile.storage_set.first().browse())

        # Rename second file in root directory
        second_file_id = FileMeta.objects.get(name='test-file-2', parent=root_directory).id
        self.user.profile.storage_set.first().rename_file(
            parent=root_directory,
            id=second_file_id,
            name='second-test-file')
        self.assertEqual(FileMeta.objects.get(id=second_file_id).name, 'second-test-file')
