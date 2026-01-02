#views.py
import requests
from django_ratelimit.decorators import ratelimit
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout,update_session_auth_hash
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import PlayerRecord, GameSession, UserProfile, BannedUser
from django.db.models import Max, Min, Sum
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.http import StreamingHttpResponse, Http404
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'index.html')

def base(request):
    return render(request,'base.html')

def how_to_play_page(request):
    return render(request,'rules.html')

def news_page(request):
    return render(request,'news.html')

@login_required(login_url='/login/')
def download_page(request):
    return render(request,'download.html')

def download_joyboard_zip(request):
    # Stream the file content from Supabase
    response = requests.get(settings.SUPABASE_SIGNED_URL, stream=True)

    if response.status_code == 200:
        # Stream it to the user
        resp = StreamingHttpResponse(response.iter_content(chunk_size=8192), content_type='application/zip')
        resp['Content-Disposition'] = 'attachment; filename="JOYBOARD_GAMEPACK.zip"'
        return resp
    else:
        raise Http404("Download not available at the moment.")

@login_required(login_url='/login/')
def contact_page(request):
    if request.method == 'POST':
        username = request.user.username
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        subject = f'New Contact Form Submission from {name}'
        message_body = f"""
Username: {username}
Full Name: {name}
Email: {email}
Message:
{message}
"""

        try:
            send_mail(
                subject,
                message_body,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],  # Sending to registered email address
                fail_silently=False,
            )
            messages.success(request, 'Your message has been sent successfully!')
        except Exception as e:
            messages.error(request, f'Sorry, error sending your message: {e}')

        return redirect('contact-html')  # Redirect after POST

    return render(request, 'contact.html')

def forgotpass_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        subject = f'Reset Password Request {username}'
        message_body = f"""
Username: {username}
Email: {email}
"""

        try:
            send_mail(
                subject,
                message_body,
                settings.EMAIL_HOST_USER,
                [settings.EMAIL_HOST_USER],  # Sending to registered email address
                fail_silently=False,
            )
            messages.success(request, 'Success! Reset details will be sent to your signup email after verification.')
        except Exception as e:
            messages.error(request, f'Sorry, error sending your message: {e}')

        return redirect('forgotpass-html')  # Redirect after POST

    return render(request, 'forgotpass.html')

@login_required(login_url='/login/')
def changepassword_logic(request):
    if request.method == 'POST':
        prev_password = request.POST.get('prev_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_new_password')
        user = request.user

        if not user.check_password(prev_password):
            messages.error(request, "Previous password is incorrect.")
        elif not new_password or not confirm_password:
            messages.error(request, "Please fill in both fields.")
        elif new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
        else:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect('dashboard-html') 

    return render(request, 'changepassword.html')


@login_required(login_url='/login/')
def dashboard_page(request):
    user = request.user
    username = user.username

    sessions = GameSession.objects.filter(username=username)
    highest_level = sessions.aggregate(Max('level_completed'))['level_completed__max'] or 0
    games_played = sessions.count()

    if highest_level < 5:
        fastest_time = None
        fastest_time_locked = True
    else:
        sessions_level_5 = sessions.filter(level_completed__gte=5)
        fastest_time = sessions_level_5.aggregate(Min('time_taken'))['time_taken__min'] or 0
        fastest_time_locked = False

    sessions_with_levels = sessions.filter(level_completed__gt=0)
    total_time = sessions_with_levels.aggregate(Sum('time_taken'))['time_taken__sum'] or 0
    total_levels = sessions_with_levels.aggregate(Sum('level_completed'))['level_completed__sum'] or 1
    average_level_time = round(total_time / total_levels, 2) if total_levels else 0

    leaderboard = PlayerRecord.objects.all().order_by('-level_completed', 'time_taken')
    current_rank = None
    for i, entry in enumerate(leaderboard, start=1):
        if entry.username == username:
            current_rank = i
            break

    highest_rank = current_rank or "—"
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    context = {
        'user_profile': profile,
        'games_played': games_played,
        'highest_level': highest_level,
        'fastest_time': fastest_time,
        'fastest_time_locked': fastest_time_locked,
        'average_time': average_level_time,
        'current_rank': current_rank or "—",
        'highest_rank': highest_rank,
        'user': user,
    }

    return render(request, 'dashboard.html', context)

@login_required
def set_description(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        description = request.POST.get('description', '')
        profile.description = description
        profile.save()
        messages.success(request, "Description updated!")
        return redirect('dashboard-html') 

    return render(request, 'description.html', {
        'user_profile': profile
    })

def leaderboard_page(request):
    # Try fetching leaderboard from Redis cache
    leaderboard = cache.get("leaderboard_cache")

    if leaderboard:
        pass
    else:
        records = PlayerRecord.objects.all().order_by('-level_completed', 'time_taken')

        leaderboard = []
        for record in records:
            user = User.objects.filter(username=record.username).first()
            profile = UserProfile.objects.filter(user=user).first() if user else None

            leaderboard.append({
                'username': record.username,
                'description': profile.description if profile else "",
                'time_taken': record.time_taken,
                'level_completed': record.level_completed,
                'input_used': record.input_used,
            })

        # Save result to cache for future requests
        cache.set("leaderboard_cache", leaderboard, timeout=60)  # cache for 1 minute

    return render(request, 'leaderboard.html', {'leaderboard': leaderboard})

def about_page(request):
    return render(request,'about.html')

def privacy_page(request):
    return render(request,'privacy.html')

def terms_page(request):
    return render(request,'terms.html')

def login_page(request):
    next_url = request.GET.get('next') or request.POST.get('next') or 'dashboard-html'

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(next_url)
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password', 'next': next_url})

    return render(request, 'login.html', {'next': next_url})


def signup_page(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')

        # Check For Banned Accounts
        if BannedUser.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'You are banned from signing up.'})
        
        if BannedUser.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': 'This email is banned.'})

        # Check normal details for new user
        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'username already exists'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'signup.html', {'error': 'email already exists for a different account'})
        
        if confirm != password:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})
        
        # Create a user if clean 
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = firstname
        user.last_name = lastname
        user.save()

        return redirect('/login')

    return render(request, 'signup.html')

def logout_page(request):
    logout(request)
    return redirect('/')


# REST API Views (for Python game and web)
@api_view(['POST'])
def api_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        return Response({'status': 'success', 'message': 'Login successful'})
    else:
        return Response({'status': 'error', 'message': 'Invalid username or password'}, status=401)

def ban_user(username, email=None):
    # Add to banned users list if not exists
    if not BannedUser.objects.filter(username=username).exists():
        BannedUser.objects.create(
            username=username,
            email=email or '',
        )

    # Delete user from PlayerRecord and Django auth_user
    PlayerRecord.objects.filter(username=username).delete()
    try:
        user = User.objects.get(username=username)
        user.delete()
    except User.DoesNotExist:
        pass

    # Send warning email
    if email:
        send_mail(
            subject="Warning: Cheating Detected",
            message=(
                f"Dear {username},\n\n"
                "We have detected suspicious activity from your account indicating possible cheating.\n"
                "If you believe this is an error, please contact us immediately.\n"
                "Otherwise, your account has been banned from our platform.\n\n"
                "Regards,\n"
                "The JoyBoard Team"
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=True,
        )

@ratelimit(key='post:username', rate="1/m", block=True)
@api_view(['POST'])
def submit_score(request):
    api_key = request.headers.get("Authorization", "").replace("Bearer ", "")
    if api_key != settings.SECRET_API_KEY:
        return Response({"error": "Unauthorized"}, status=401)

    username = request.data.get('username')
    try:
        user = User.objects.get(username=username)
        email = user.email
    except User.DoesNotExist:
        email = None
    time_taken = float(request.data.get('time_taken', 0))
    level_completed = int(request.data.get('level_completed', 0))
    input_used = request.data.get('input_used')

    # Basic sanity check
    if level_completed < 0 or level_completed > 5 or time_taken < 0 or time_taken > 2000:
        ban_user(username, email)
        return Response(
            {'error': 'Cheating detected. Your account has been banned. Kindly check your email, including spam, for details.'},
            status=403
        )

    # Check suspiciously low time for specific levels
    if (level_completed == 1 and time_taken <= settings.LEVEL1_TIME) or \
    (level_completed == 2 and time_taken <= settings.LEVEL2_TIME) or \
    (level_completed == 3 and time_taken <= settings.LEVEL3_TIME) or \
    (level_completed == 4 and time_taken <= settings.LEVEL4_TIME) or \
    (level_completed == 5 and time_taken <= settings.LEVEL5_TIME):
        ban_user(username, email)
        return Response(
            {'error': 'Cheating detected. Your account has been banned. Kindly check your email, including spam, for details.'},
            status=403
        )

    # Submit score logic - if not cheated
    try:
        record = PlayerRecord.objects.get(username=username)

        if level_completed > record.level_completed:
            record.level_completed = level_completed
            record.time_taken = time_taken
            record.input_used = input_used
            record.save()
            message = 'Record updated (better level)!'
        elif level_completed == record.level_completed and time_taken < record.time_taken:
            record.time_taken = time_taken
            record.input_used = input_used
            record.save()
            message = 'Record updated (faster time)!'
        else:
            message = 'No update. Previous record is better.'
    except PlayerRecord.DoesNotExist:
        PlayerRecord.objects.create(
            username=username,
            time_taken=time_taken,
            level_completed=level_completed,
            input_used=input_used
        )
        message = 'New player record created!'

    GameSession.objects.create(
        username=username,
        time_taken=time_taken,
        level_completed=level_completed,
    )

    # After saving a new PlayerRecord
    cache.delete("leaderboard_data")  # next request will recompute leaderboard

    return Response({'message': message}, status=201)

@api_view(['POST'])
def get_config(request):
    data = {
        "MAX_LEVEL": settings.MAX_LEVEL,
        "HORIZANTAL_ACC": settings.HORIZANTAL_ACC,
        "HORIZANTAL_FRICTION": settings.HORIZANTAL_FRICTION,
        "VERTICAL_ACC": settings.VERTICAL_ACC,
        "VERTICAL_JUMP_SPEED": settings.VERTICAL_JUMP_SPEED,
        "MAX_HORIZANTAL_SPEED": settings.MAX_HORIZANTAL_SPEED,
        "TERM_VELOCITY": settings.TERM_VELOCITY,
        "SHOOTING_SPEED": settings.SHOOTING_SPEED,
        "BULLET_SPEED": settings.BULLET_SPEED,
        "HEALTH_BAR_VALUE": settings.HEALTH_BAR_VALUE,
        "IMMUNITY_BAR_VALUE": settings.IMMUNITY_BAR_VALUE,
        "JUMP_IMMUNITY_COST": settings.JUMP_IMMUNITY_COST,
        "BULLET_IMMUNITY_COST": settings.BULLET_IMMUNITY_COST,
        "IMMUNITY_REGEN_RATE": settings.IMMUNITY_REGEN_RATE,
        "LAVA_DAMAGE_AMOUNT": settings.LAVA_DAMAGE_AMOUNT,
        "MAX_LAVA_DAMAGE_COOLDOWN": settings.MAX_LAVA_DAMAGE_COOLDOWN,
        "ENEMY_SHOOT_RANGE": settings.ENEMY_SHOOT_RANGE,
        "MIN_ENEMY_SHOOT_COOLDOWN": settings.MIN_ENEMY_SHOOT_COOLDOWN,
        "MAX_ENEMY_SHOOT_COOLDOWN": settings.MAX_ENEMY_SHOOT_COOLDOWN,
        "ENEMY_MELEE_DAMAGE": settings.ENEMY_MELEE_DAMAGE,
        "ENEMY_BULLET_DAMAGE": settings.ENEMY_BULLET_DAMAGE,
        "COLLECTABLE_SPAWN_ATTEMPTS": settings.COLLECTABLE_SPAWN_ATTEMPTS,
        "COLLECTABLE_MIN_DIST_FROM_ENEMY_TILE": settings.COLLECTABLE_MIN_DIST_FROM_ENEMY_TILE,

        "API_KEY":settings.SECRET_API_KEY,
        "HOSTED_LOGIN_URL":settings.API_LOGIN_PATH,
        "HOSTED_SUBMIT_URL":settings.API_SUBMIT_SCORE_PATH,

    }
    return Response(data)