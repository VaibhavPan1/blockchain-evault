from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPES = [
        ('client', 'Client'),
        ('lawyer', 'Lawyer'),
        ('court', 'Court'),
    ]
    user_type = models.CharField(max_length=6, choices=USER_TYPES, default='client')

    @property
    def full_name(self):
        """Returns the user's full name by combining first_name and last_name."""
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return self.username
    
class File(models.Model):
    file_name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    cid = models.CharField(max_length=255)


class PublicKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    public_key = models.TextField()

class PrivateKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    encrypted_private_key = models.TextField()


class FileKey(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    encrypted_aes_key = models.TextField()

class FileIPFS(models.Model):
    file = models.OneToOneField(File, on_delete=models.CASCADE)
    ipfs_cid = models.CharField(max_length=255)
    blockchain_tx_hash = models.CharField(max_length=255)
    smart_contract_filename = models.CharField(max_length=255)

class FileAccessLog(models.Model):
    ACTION_CHOICES = (
        ('viewed', 'Viewed'),
        ('downloaded', 'Downloaded'),
        ('decrypted', 'Decrypted'),
    )

    file = models.ForeignKey(File, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    accessed_at = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
