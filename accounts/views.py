from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.utils.html import strip_tags

import requests
import requests.utils

from .forms import (
    RegistrationForm,
    UserProfileForm,
    UserForm,
)
from .models import Account, UserProfile
from .utils import email_token_generator
from carts.models import Cart, CartItem
from carts.views import _cart_id
from orders.models import Order, OrderProduct


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            
            # Create a new user
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password,
            )
            user.phone_number = phone_number
            user.save()
            
            # Create user profile
            profile = UserProfile()
            profile.user_id = user.id
            profile.profile_picture = 'default/default-user.png'
            profile.save()
            
            # User Activation
            current_site = get_current_site(request)
            mail_subject = 'Please activate your account.'
            message = render_to_string('accounts/verification_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),          # nobody can see the primary key.
                'token': default_token_generator.make_token(user)
                # 'token': email_token_generator.make_token(user)
                
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.content_subtype = 'html'                             # specify type of the message.
            send_email.send()
            
            # messages.success(request, 'We sent you a verification email.Please verify it.')
            return redirect('/accounts/login/?command=verification&email='+email)
            
    else:   
        form = RegistrationForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        user = auth.authenticate(email=email, password=password)
        
        if user is not None:
            # user have a cart before login condition.
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))       # Create a sessionID
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    
                    # Getting the product variations by cart id.
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))
                        
                    # Get the cart item from the user to acess the product variations
                    cart_item = CartItem.objects.filter(user=user)
            
                    existing_variations_list = []
                    id_list = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        existing_variations_list.append(list(existing_variation))
                        id_list.append(item.id)
                    
                    for product in product_variation:
                        if product in existing_variations_list:
                            index = existing_variations_list.index(product)      # index of the common item.
                            item_id = id_list[index]
                            item = CartItem.objects.get(id=item_id)
                            
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            
                            for item in cart_item:
                                item.user = user
                                item.save()
            except:
                pass
            
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            
            url = request.META.get('HTTP_REFERER')
            try:
                print('URL -> ', url)
                query = requests.utils.urlparse(url).query            # next=/cart/checkout/                  
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('dashboard')
            
            
        else:
            messages.error(request, 'Invalid login credentials.')
            
            return redirect('login')
            
        
        
    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are logged out.')
    
    return redirect('login')


def activate(request, uidb64, token):
    # return HttpResponse('ok')
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'congratulations! your account is activated.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('register')
    

@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    orders_count = orders.count()
    
    user_profile = UserProfile.objects.get(user_id=request.user.id)
    
    context = {
        'orders_count': orders_count,
        'user_profile': user_profile,
    }
    
    return render(request, 'accounts/dashboard.html', context)


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__iexact=email)
            
            # Reset password email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password.'
            message = render_to_string('accounts/reset-password-email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),          
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.content_subtype = 'html'                            
            send_email.send()
            
            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
            
        else:
            messages.error(request, 'Account does not exist.')
            return redirect('forgot-password')
            
    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
        
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please enter your password.')
        return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired.')
        return redirect('login')
    
    
def reset_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)           # set password and hash it.
            user.save()
            messages.success(request, 'password reset successful.')
            return redirect('login')
            
        else:
            messages.error(request, 'Passwords do not match!')
            return redirect('reset_password')
        
    else:
        return render(request, 'accounts/reset_password.html')
    

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True)
    
    context = {
        'orders': orders
    }
    
    return render(request, 'accounts/my_orders.html', context)


@login_required(login_url='login')
def edit_profile(request):
    user_profile_instance  = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile_instance)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('edit_profile')
    else:
        # If the request not a POST, then render the form with the data.
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile_instance)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_profile': user_profile_instance,
    }
    
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        
        user = Account.objects.get(username__iexact=request.user.username)
        
        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                auth.logout(request)
                messages.success(request, 'password changed successfully.') 
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter valid current password.')
                return redirect('change_password')
        else:
            messages.error(request, 'Password does not match.')
            return redirect('change_password')
        
    return render(request, 'accounts/change_password.html')

@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    
    sub_total = 0
    for i in order_detail:
        sub_total += i.product * i.quantity
    
    context = {
        'order_detail': order_detail,
        'order': order,
        'sub_total': sub_total,
    }
    
    return render(request, 'accounts/order_detail.html', context)