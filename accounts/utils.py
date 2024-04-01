from datetime import datetime, timedelta
import cryptography
from cryptography.fernet import Fernet

from django.contrib.auth.tokens import PasswordResetTokenGenerator

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    
    def _make_hash_value(self, user, timestamp):
        return (
                str(user.is_active) + str(user.pk) + str(timestamp)
        )


email_token_generator = EmailVerificationTokenGenerator()


# class ExpiringTokenGenerator:
#     FERNET_KEY = 'H-gvBa31So7ZWRlIleY7q5xYPIytGnRHRcBpRbASyao='
#     fernet = Fernet(FERNET_KEY)

#     DATE_FORMAT = '%Y-%m-%d %H-%M-%S'
#     EXPIRATION_MINUTES = 3

#     def _get_time(self):
#         """Returns a string with the current UTC time"""
#         return datetime.utcnow().strftime(self.DATE_FORMAT)

#     def _parse_time(self, d):
#         """Parses a string produced by _get_time and returns a datetime object"""
#         return datetime.strptime(d, self.DATE_FORMAT)

#     def generate_token(self, text):
#         """Generates an encrypted token"""
#         full_text = text + '|' + self._get_time()
#         token = self.fernet.encrypt(bytes(full_text))

#         return token

#     def get_token_value(self, token):
#         """Gets a value from an encrypted token.
#         Returns None if the token is invalid or has expired.
#         """
#         try:
#             value = self.fernet.decrypt(bytes(token))
#             separator_pos = value.rfind('|')

#             text = value[: separator_pos]
#             token_time = self._parse_time(value[separator_pos + 1: ])
            
#             if token_time + timedelta(minutes=self.EXPIRATION_MINUTES) < datetime.utcnow():
#                 return None

#         except cryptography.fernet.InvalidToken:
#             return None

#         return text 

#     def is_valid_token(self, token):
#         return self.get_token_value(token) is not None
    
    
# expiring_token = ExpiringTokenGenerator()