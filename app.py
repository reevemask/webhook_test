from flask import Flask, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

# 텔레그램 봇 설정
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID_HERE')

def send_telegram_message(message):
    """텔레그램으로 메시지 전송"""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, data=data, timeout=10)
        return response.status_code == 200
        
    except Exception as e:
        print(f"텔레그램 전송 오류: {str(e)}")
        return False

@app.route('/', methods=['GET'])
def home():
    """서버 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'message': '텔레그램 웹훅 서버가 정상 작동중입니다!',
        'time': datetime.now().isoformat(),
        'endpoints': ['/test', '/webhook', '/webhook/test']
    })

@app.route('/test', methods=['GET'])
def test_telegram():
    """텔레그램 연결 테스트"""
    test_message = f"""
🧪 텔레그램 연결 테스트

✅ 웹훅 서버 작동 중
⏰ 시간: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
🤖 상태: 정상

이 메시지가 보이면 설정이 완료되었습니다! 🎉
"""
    
    success = send_telegram_message(test_message)
    
    if success:
        return jsonify({
            'status': 'success',
            'message': '텔레그램 테스트 메시지 전송 완료!'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': '텔레그램 전송 실패. 토큰과 채팅 ID를 확인하세요.'
        }), 400

@app.route('/webhook', methods=['POST'])
def webhook():
    """TradingView 웹훅 수신"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
            
        print(f"웹훅 데이터 수신: {data}")
        
        # 간단한 메시지 포맷
        message = f"""
📊 TradingView 신호 수신

⏰ 시간: {datetime.now().strftime("%H:%M:%S")}
📈 데이터: {data}
"""
        
        success = send_telegram_message(message)
        
        if success:
            return jsonify({'status': 'success', 'message': '알림 전송 완료'})
        else:
            return jsonify({'status': 'error', 'message': '전송 실패'}), 500
            
    except Exception as e:
        print(f"웹훅 처리 오류: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
