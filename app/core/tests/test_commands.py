from unittest.mock import patch
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase

class CommandTests(TestCase):
    
    def test_wait_for_db_ready(self):
        """
        Test waiting for db when db is available
        """
        # Mock the behavior of __getitem__
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db') # wait_for_db is the name of management command we create
            self.assertEqual(gi.call_count, 1)
        
    @patch('time.sleep', return_value=True)    
    def test_wait_for_db(self, ts):
        """
        Test waiting for db
        """
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # The first 5 times we call this __getitem__ raise OperationalError,
            # Then the 6th time it will complete
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
        