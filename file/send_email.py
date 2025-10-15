import smtplib
import json
import os
import sys # 오류 발생 시 워크플로우를 '실패'로 만들기 위해 필수
from email.mime.text import MIMEText
from datetime import datetime

def send_notification_email():
    log_message = ""
    try:
        # --- 1. GitHub Secrets에서 SMTP 정보 가져오기 ---
        smtp_server = os.environ.get('SMTP_SERVER')
        smtp_port = int(os.environ.get('SMTP_PORT'))
        sender_email = os.environ.get('SMTP_USERNAME')
        sender_password = os.environ.get('SMTP_PASSWORD')

        if not all([smtp_server, smtp_port, sender_email, sender_password]):
            raise ValueError("SMTP 설정 Secret 값이 하나 이상 없습니다.")

        # --- 2. config.json 파일에서 메일 내용 읽기 ---
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)

        recipient_email = config['email']
        location = ', '.join(config['location'])
        year = config['year']
        jobs = ', '.join(config['jobs'])

        # --- 3. 이메일 내용 생성 ---
        subject = f"🚀 [{location}] 지역 채용 정보 자동화 알림"
        body = f"""안녕하세요. 요청하신 채용 정보 자동화 알림입니다.
- 검색 지역: {location}
- 요구 경력: {year}년 이상
- 관심 직무: {jobs}"""

        msg = MIMEText(body, 'plain', 'utf-8')
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # --- 4. SMTP 서버로 이메일 발송 ---
        print("SMTP 서버에 연결하여 로그인을 시도합니다...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        log_message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ 메일 발송 성공: {recipient_email}로 전송 완료.\n"
        print(log_message)

    except Exception as e:
        # --- 🚨 여기가 핵심! 오류 발생 시 워크플로우를 실패 처리 ---
        log_message = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 메일 발송 실패\n"
        print(log_message)
        print("---!!! 진짜 오류 메시지 !!!---")
        print(e) # 실제 오류 내용을 로그에 출력
        print("---------------------------")
        with open('log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(log_message + str(e) + "\n")
        sys.exit(1) # 이 명령어로 워크플로우를 '실패' 상태로 만듦

    # 성공했을 때만 로그 기록
    with open('log.txt', 'a', encoding='utf-8') as log_file:
        log_file.write(log_message)

if __name__ == "__main__":
    send_notification_email()