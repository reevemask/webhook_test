from flask import Flask, request, jsonify
import requests
import os
import json
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

def format_fibonacci_message(data):
    """피보나치 신호 메시지 포맷팅"""
    try:
        action = data.get('action')
        symbol = data.get('symbol', 'Unknown')
        current_time = datetime.now().strftime("%H:%M:%S")
        
        if action == 'ENTRY':
            price = float(data.get('price', 0))
            tp = float(data.get('tp', 0))
            sl = float(data.get('sl', 0))
            fib_type = data.get('fib_type', '')
            
            # 수익률 계산
            tp_rate = ((tp - price) / price) * 100
            sl_rate = ((sl - price) / price) * 100
            
            message = f"""🚀 <b>피보나치 진입 신호</b>

📈 <b>심볼:</b> {symbol}
🎯 <b>피보나치:</b> {fib_type} 되돌림
💰 <b>진입가:</b> {price:,.0f}
📊 <b>익절가:</b> {tp:,.0f} (+{tp_rate:.1f}%)
🛑 <b>손절가:</b> {sl:,.0f} ({sl_rate:.1f}%)
⏰ <b>시간:</b> {current_time}

📋 위험 관리를 잊지 마세요!"""

        elif action == 'EXIT':
            exit_price = float(data.get('exit_price', 0))
            entry_price = float(data.get('entry_price', 0))
            result = data.get('result', '')
            profit_rate = float(data.get('profit_rate', 0))
            
            emoji = "✅" if result == "PROFIT" else "🛑"
            result_text = "익절" if result == "PROFIT" else "손절"
            
            message = f"""{emoji} <b>피보나치 종료 신호</b>

📈 <b>심볼:</b> {symbol}
🔥 <b>결과:</b> {result_text}
💰 <b>진입가:</b> {entry_price:,.0f}
🎯 <b>종료가:</b> {exit_price:,.0f}
📊 <b>수익률:</b> {profit_rate:+.2f}%
⏰ <b>시간:</b> {current_time}

{emoji} 거래 완료되었습니다."""

        else:
            # 알 수 없는 액션의 경우 원본 데이터 출력
            message = f"""📊 <b>TradingView 신호</b>

⏰ <b>시간:</b> {current_time}
📋 <b>데이터:</b> {json.dumps(data, indent=2)}"""

        return message
        
    except Exception as e:
        print(f"메시지 포맷팅 오류: {str(e)}")
        # 오류 발생 시 기본 메시지 반환
        return f"""📊 <b>TradingView 신호 (포맷 오류)</b>

⏰ <b>시간:</b> {datetime.now().strftime("%H:%M:%S")}
📋 <b>원본 데이터:</b> {json.dumps(data, indent=2)}
⚠️ <b>오류:</b> {str(e)}"""

@app.route('/', methods=['GET'])
def home():
    """서버 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'message': '피보나치 텔레그램 웹훅 서버가 정상 작동중입니다!',
        'time': datetime.now().isoformat(),
        'endpoints': ['/test', '/webhook', '/webhook/test', '/webhook/test-exit']
    })

@app.route('/test', methods=['GET'])
def test_telegram():
    """텔레그램 연결 테스트"""
    test_message = f"""🧪 <b>텔레그램 연결 테스트</b>

✅ 웹훅 서버 작동 중
⏰ 시간: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
🤖 상태: 정상

이 메시지가 보이면 설정이 완료되었습니다! 🎉"""
    
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
        # JSON 데이터 파싱 시도
        try:
            data = request.get_json()
        except:
            # JSON 파싱 실패 시 텍스트로 시도
            raw_data = request.get_data(as_text=True)
            try:
                data = json.loads(raw_data)
            except:
                # 여전히 실패하면 원본 텍스트 사용
                data = {'raw_message': raw_data}
        
        if not data:
            return jsonify({'error': 'No data received'}), 400
            
        print(f"웹훅 데이터 수신: {data}")
        
        # 피보나치 신호 메시지 포맷팅
        message = format_fibonacci_message(data)
        
        success = send_telegram_message(message)
        
        if success:
            return jsonify({'status': 'success', 'message': '알림 전송 완료'})
        else:
            return jsonify({'status': 'error', 'message': '전송 실패'}), 500
            
    except Exception as e:
        print(f"웹훅 처리 오류: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/test', methods=['GET', 'POST'])
def webhook_test():
    """웹훅 테스트 엔드포인트"""
    test_entry_data = {
        "action": "ENTRY",
        "symbol": "BTCUSDT",
        "price": 45000.0,
        "tp": 46200.0,
        "sl": 44100.0,
        "fib_type": "0.382",
        "time": "1709467200000"
    }
    
    message = format_fibonacci_message(test_entry_data)
    success = send_telegram_message(message)
    
    if success:
        return jsonify({'status': 'success', 'message': '테스트 진입 신호 전송 완료!'})
    else:
        return jsonify({'status': 'error', 'message': '테스트 전송 실패'}), 500

@app.route('/webhook/test-exit', methods=['GET', 'POST'])
def webhook_test_exit():
    """웹훅 종료 신호 테스트 엔드포인트"""
    test_exit_data = {
        "action": "EXIT",
        "symbol": "BTCUSDT",
        "exit_price": 46150.0,
        "entry_price": 45000.0,
        "result": "PROFIT",
        "profit_rate": "25.56",
        "time": "1709467800000"
    }
    
    message = format_fibonacci_message(test_exit_data)
    success = send_telegram_message(message)
    
    if success:
        return jsonify({'status': 'success', 'message': '테스트 종료 신호 전송 완료!'})
    else:
        return jsonify({'status': 'error', 'message': '테스트 전송 실패'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
