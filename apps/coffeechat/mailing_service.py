from django.http import JsonResponse

from apps.coffeechat.models import CoffeeChat
from django.utils.html import strip_tags
from django.core.mail import send_mail


def send_request_mail(form, profile, request):
    message = form.cleaned_data['requestContent']
    subject = "PiroTime: 커피챗 신청이 왔습니다!"
    content = f"{profile.user}님! 작성하신 커피챗 프로필에 요청한 사람이 있습니다. 아래 링크로 들어와 확인해 보세요: <a href='https://www.pirotime.com'>www.pirotime.com</a>"
    sending_mail(profile.user, request.user, subject, content, message)
    CoffeeChat.objects.create(
        user=request.user,
        profile=profile,
        status='WAITING',
        letterToSenior=message
    )

def send_accept_mail(coffeechat_request, profile, request):
    subject = f"PiroTime: {request.user}님이 커피챗 요청을 수락했습니다!"
    content = f"{coffeechat_request.user}님! 요청하신 커피챗 요청이 수락되었습니다! 아래에 있는 연락처로 연락해보세요!"
    message = ""
    try:
        sending_mail(profile.user, coffeechat_request.user, subject, content, message)
    except Exception as e:
        return JsonResponse({"error": "메일을 보내는 중 문제가 발생했습니다."}, status=503)
    return JsonResponse({"status": "accepted"})

def send_reject_mail(coffeechat_request, profile, request):
    subject = f"PiroTime: {request.user}님이 커피챗 요청을 거절하셨습니다!"
    message = f"{coffeechat_request.user}님! 선배님의 개인 사정으로 인해 커피챗 요청이 거절되었습니다. 다른 선배님과의 커피챗은 어떠하신가요?"
    content = ""
    try:
        sending_mail(profile.user, coffeechat_request.user, subject, content, message)
        return JsonResponse({"status": "rejected"})
    except Exception as e:
        return JsonResponse({"error": "메일을 보내는 중 문제가 발생했습니다."}, status=503)


def sending_mail(receiver, sender, subject, content, message):
    from_email = 'pirotimeofficial@gmail.com'
    recipient_list = [receiver.email]

    # HTML 메시지 직접 생성
    html_message = f"""
    <div style="padding: 20px; background-color: #f9f9f9;">
        <h2 style="color: #333;">PiroTime 커피챗</h2>
        <h3 style="color: #444;">{content}</h3>
        <p style="margin: 15px 0;">{message}</p>
        <hr style="border: 1px solid #eee;">
        <p style="color: #666;">From: {sender.username}</p>
        <p style="color: #666;">To: {receiver.username}</p>
    </div>
    """

    plain_message = strip_tags(html_message)
    send_mail(
        subject,
        plain_message,
        from_email,
        recipient_list,
        html_message=html_message,
    )
    return True


# def generate_email_content(sender, receiver):
#     subject = "PiroTime: 커피챗 신청이 왔습니다!"
#     message = f"{sender.username}님으로 부터 협력 제안이 왔습니다. PiroTime에 접속해서 내용을 확인하세요!"
#     from_email = 'pirotimeofficial@gmail.com'
#     recipient_list = [receiver.email]
#     return subject, message, from_email, recipient_list
