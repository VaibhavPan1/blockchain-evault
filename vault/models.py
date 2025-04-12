from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('judge', 'Judge'),
        ('lawyer', 'Lawyer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)


class PublicKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    public_key = models.TextField()

class PrivateKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    encrypted_private_key = models.TextField()

class File(models.Model):
    file_name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    original_file_name = models.CharField(max_length=255)
    encrypted_file_path = models.CharField(max_length=255)

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
