from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PublicKey, PrivateKey, File, FileKey, FileIPFS, FileAccessLog

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role Info', {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role',)

@admin.register(PublicKey)
class PublicKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'public_key')

@admin.register(PrivateKey)
class PrivateKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'encrypted_private_key')

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'uploaded_by', 'uploaded_at')

@admin.register(FileKey)
class FileKeyAdmin(admin.ModelAdmin):
    list_display = ('file', 'user', 'encrypted_aes_key')

@admin.register(FileIPFS)
class FileIPFSAdmin(admin.ModelAdmin):
    list_display = ('file', 'ipfs_cid', 'blockchain_tx_hash')

@admin.register(FileAccessLog)
class FileAccessLogAdmin(admin.ModelAdmin):
    list_display = ('file', 'user', 'action', 'accessed_at')
    list_filter = ('action',)
