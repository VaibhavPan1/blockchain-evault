from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from pathlib import Path

from .ipfs_module.ipfs_handler import IPFSHandler
from .eth_module.contract_handler import ContractHandler
from .db_module.db_handler import DBHandler
from .models import File
import json
import os
import uuid



ipfs_handler = IPFSHandler()
# db_handler = DBHandler(host="localhost", user='root', password='1312', database='web3')
contract_handler = ContractHandler()

BASE_DIR = Path(__file__).resolve().parent

abi = [
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "fileName",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "fileHash",
                "type": "string"
            }
        ],
        "name": "storeFile",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "fileName",
                "type": "string"
            }
        ],
        "name": "getFileHash",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "name": "fileHashes",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]
contract_address = "0xb2100aDf3B5b8c48D2224f0B23095e8c58933E37"


def register_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user_type = request.POST.get('user_type')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        # Check if username already exists
        if get_user_model().objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('register')

        # Split name into first and last name
        first_name = ''
        last_name = ''
        if name:
            name_parts = name.split(' ', 1)
            first_name = name_parts[0]
            if len(name_parts) > 1:
                last_name = name_parts[1]

        # Create the user
        user = get_user_model().objects.create(
            username=username,
            email=email,
            password=make_password(password),
            user_type=user_type,
            first_name=first_name,
            last_name=last_name,
        )
        user.save()

        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')

    return render(request, 'vault/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirect to home or dashboard page
        else:
            print("Invalid username or password")
            messages.error(request, 'Invalid username or password')
            return redirect('login')

    return render(request, 'vault/login.html')

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'vault/dashboard.html')

def index(request):
    return render(request, 'vault/index.html')


@login_required
def upload(request):
    if request.method == 'POST':
        confirm = request.POST.get('confirm')
        filename = request.POST.get('filename')

        # If this is a confirmation POST (i.e., replacing an existing file)
        if confirm == 'yes' and filename:
            temp_path = BASE_DIR / 'temp' / filename
            if not temp_path.exists():
                return HttpResponse("❌ Temporary file not found. Please re-upload.")

            try:
                cid = ipfs_handler.upload_file(temp_path)
                os.remove(temp_path)

                existing_file = File.objects.get(file_name=filename, uploaded_by=request.user)
                existing_file.cid = cid
                existing_file.save()

                contract_handler.store_file_hash(filename, cid, abi, contract_address)

                return render(request, 'vault/upload.html', {
                    'status': f"✅ File '{filename}' replaced successfully. CID: {cid}"
                })
            except Exception as e:
                return HttpResponse(f"❌ Error uploading file: {e}")

        # If this is a fresh file upload
        elif 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            filename = uploaded_file.name
            file_path = BASE_DIR / 'temp' / filename

            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            # Check for existing file
            existing_file = File.objects.filter(file_name=filename, uploaded_by=request.user).first()
            if existing_file:
                return render(request, 'vault/confirm_replace.html', {'filename': filename})

            try:
                cid = ipfs_handler.upload_file(file_path)
                os.remove(file_path)

                File.objects.create(file_name=filename, uploaded_by=request.user, cid=cid)
                contract_handler.store_file_hash(filename, cid, abi, contract_address)

                return render(request, 'vault/upload.html', {
                    'status': f"✅ File '{filename}' uploaded successfully. CID: {cid}"
                })
            except Exception as e:
                return HttpResponse(f"❌ Error uploading file: {e}")

        # Neither file nor confirmation — invalid POST
        else:
            return HttpResponse("❌ Invalid form submission. No file or confirmation received.")

    return render(request, 'vault/upload.html')

@login_required(login_url='login')
def view_files(request):
    if request.user.is_authenticated:
        files = File.objects.filter(uploaded_by=request.user)
        return render(request, 'vault/viewfiles.html', {'files': files})
    else:
        return redirect('login')
    


@login_required
def retrieve_file(request, file_name, cid):
    try:
        # Step 1: Fetch file that matches file_name, cid, and belongs to the current user
        file_obj = File.objects.get(file_name=file_name, cid=cid, uploaded_by=request.user)
    except File.DoesNotExist:
        print(f"File not found for user {request.user.username} with file_name={file_name} and cid={cid}")
        raise Http404("File not found or unauthorized access.")

    # Step 2: Validate with Smart Contract
    contract_cid = contract_handler.retrieve_file_hash(
        file_name=file_name,
        abi=abi,
        contract_address=contract_address
    )

    print(f"CID from DB: {file_obj.cid}")
    print(f"CID from Contract: {contract_cid}")

    if contract_cid and file_obj.cid == contract_cid:
        # Step 3: Fetch from IPFS
        file_content = ipfs_handler.get_file(cid)

        # Step 4: Serve as download
        response = HttpResponse(file_content, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response
    else:
        print("CID mismatch or file not verified on blockchain.")
        raise Http404("File validation failed.")
    


@login_required
def profile(request):
    return render(request, 'vault/profile.html')

@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        # Fetch data from POST request
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        user_type = request.POST.get('user_type', '').strip()

        # Sanity Checks
        if not first_name or not last_name or not email or not user_type:
            messages.error(request, "All fields are required.")
            return redirect('edit_profile')

        # if user_type not in dict(User.USER_TYPES):
        #     messages.error(request, "Invalid user type selected.")
        #     return redirect('edit_profile')

        # Update user model fields
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.user_type = user_type
        user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('edit_profile')

    # GET Request
    # context = {
    #     'user': user,
    #     'user_types': User.USER_TYPES
    # }
    return render(request, 'vault/edit_profile.html')

@login_required
def change_password(request):
    
    return render(request, 'vault/change_password.html')
